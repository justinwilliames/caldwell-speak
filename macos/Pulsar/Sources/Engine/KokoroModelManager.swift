import Foundation
import Kokoro
import Observation

/// Downloads, verifies and removes the Kokoro model — the thing behind the
/// "Download Kokoro" button in Settings.
///
/// Why this exists rather than `VoiceDownloader` alone: the upstream downloader
/// fetches with no progress reporting and no atomic write. That is fine for a CLI
/// and wrong for a 310MB transfer in a menu-bar app, where the user needs to see
/// movement, be able to cancel, and never end up with a half-file that reads as
/// installed. `VoiceDownloader.defaultBaseURL` is still the single source of truth
/// for WHERE the files come from — only the transfer is reimplemented.
///
/// Files fetched (into Application Support, not Caches — see KokoroVoiceClient):
///   config.json                 ~2 KB
///   kokoro-v1_0.safetensors   ~310 MB
///   voices/<9 cast voices>.npy  ~4.6 MB
@Observable
@MainActor
final class KokoroModelManager {

    static let shared = KokoroModelManager()

    enum Phase: Equatable {
        case notInstalled
        case downloading(fraction: Double)
        case installed
        case failed(String)
    }

    private(set) var phase: Phase = .notInstalled

    /// Bytes we expect to move, for the progress bar. Weights dominate; the exact
    /// total only has to be close enough for the bar to look honest.
    private static let expectedTotalBytes =
        KokoroVoiceClient.expectedWeightsBytes           // model
        + 522_368 * 9                                    // 9 cast voices @ 510 KiB
        + 2_351                                          // config.json

    private var task: Task<Void, Never>?

    private init() {
        phase = KokoroVoiceClient.isInstalled() ? .installed : .notInstalled
    }

    /// Re-derive state from disk. Called when Settings appears, so a download that
    /// completed in a previous launch (or a folder the user deleted by hand) is
    /// reflected rather than remembered.
    func refresh() {
        guard task == nil else { return }   // never stomp an in-flight download
        phase = KokoroVoiceClient.isInstalled() ? .installed : .notInstalled
    }

    var isBusy: Bool { task != nil }

    // MARK: - Download

    func download() {
        guard task == nil else { return }
        phase = .downloading(fraction: 0)
        task = Task { [weak self] in
            guard let self else { return }
            do {
                try await self.runDownload()
                self.task = nil
                // Trust the same strict check the speak path uses, not "the
                // transfer returned without throwing".
                if KokoroVoiceClient.isInstalled() {
                    self.phase = .installed
                    KokoroVoiceClient.warm()
                } else {
                    self.phase = .failed("Download finished but the model is incomplete.")
                }
            } catch is CancellationError {
                self.task = nil
                self.phase = KokoroVoiceClient.isInstalled() ? .installed : .notInstalled
            } catch {
                self.task = nil
                self.phase = .failed(error.localizedDescription)
            }
        }
    }

    func cancel() {
        task?.cancel()
        task = nil
    }

    private func runDownload() async throws {
        let dir = KokoroVoiceClient.modelDirectory
        let voicesDir = dir.appendingPathComponent(
            ConvertedWeightsLayout.voicesDirectoryName, isDirectory: true)
        try FileManager.default.createDirectory(at: voicesDir, withIntermediateDirectories: true)

        let base = VoiceDownloader.defaultBaseURL
        var moved = 0

        // Small files first: if the network or the repo is broken, fail in a second
        // rather than 310MB later.
        try await fetch("\(base)/MLX_GPU/config.json",
                        to: KokoroVoiceClient.configURL, movedSoFar: &moved)

        for voice in KokoroVoiceClient.requiredVoices {
            try Task.checkCancellation()
            try await fetch("\(base)/MLX_GPU/voices/\(voice).npy",
                            to: voicesDir.appendingPathComponent("\(voice).npy", isDirectory: false),
                            movedSoFar: &moved)
        }

        try Task.checkCancellation()
        try await fetch("\(base)/MLX_GPU/\(ConvertedWeightsLayout.modelFileName)",
                        to: ConvertedWeightsManifest(directory: dir).modelURL,
                        movedSoFar: &moved)
    }

    /// Download one file to `destination`, updating `phase` as bytes land.
    ///
    /// Uses a real `URLSessionDownloadTask` (via the async `download(from:delegate:)`),
    /// NOT `URLSession.bytes`. `bytes` is an AsyncSequence of individual UInt8s —
    /// 310 million awaits for the weights file, which is slower than the network by
    /// orders of magnitude. The download task streams to its own temp file and
    /// reports progress through the delegate.
    ///
    /// URLSession hands back a temp file it deletes on return, so the move into
    /// place happens inside this call. A cancelled or failed transfer therefore
    /// never leaves anything at `destination` for `isInstalled()` to miscount.
    private func fetch(_ urlString: String, to destination: URL, movedSoFar: inout Int) async throws {
        guard let url = URL(string: urlString) else {
            throw DownloadError.badURL(urlString)
        }
        let already = movedSoFar
        let progress = DownloadProgressDelegate { [weak self] written in
            Task { @MainActor in
                guard let self else { return }
                self.phase = .downloading(
                    fraction: min(1, Double(already + written) / Double(Self.expectedTotalBytes)))
            }
        }

        let (tempURL, response) = try await URLSession.shared.download(from: url, delegate: progress)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            try? FileManager.default.removeItem(at: tempURL)
            throw DownloadError.http((response as? HTTPURLResponse)?.statusCode ?? -1, urlString)
        }
        if Task.isCancelled {
            try? FileManager.default.removeItem(at: tempURL)
            throw CancellationError()
        }

        let attrs = try? FileManager.default.attributesOfItem(atPath: tempURL.path)
        let size = (attrs?[.size] as? Int) ?? 0
        try? FileManager.default.removeItem(at: destination)
        try FileManager.default.moveItem(at: tempURL, to: destination)
        movedSoFar += size
        phase = .downloading(
            fraction: min(1, Double(movedSoFar) / Double(Self.expectedTotalBytes)))
    }

    /// Bridges `URLSessionDownloadTask`'s byte-progress callback to a closure.
    /// `didFinishDownloadingTo` is required by the protocol but unused — the async
    /// `download(from:delegate:)` returns the file itself.
    private final class DownloadProgressDelegate: NSObject, URLSessionDownloadDelegate, @unchecked Sendable {
        private let onProgress: @Sendable (Int) -> Void

        init(onProgress: @escaping @Sendable (Int) -> Void) {
            self.onProgress = onProgress
        }

        func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                        didWriteData bytesWritten: Int64, totalBytesWritten: Int64,
                        totalBytesExpectedToWrite: Int64) {
            onProgress(Int(totalBytesWritten))
        }

        func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                        didFinishDownloadingTo location: URL) {}
    }

    // MARK: - Remove

    /// Delete the download and fall back to `say`. Flips the engine too — leaving
    /// `voiceEngine == .kokoro` with no model on disk would mean every line takes
    /// the fallback path forever, which looks like Kokoro simply not working.
    func delete() {
        cancel()
        KokoroVoiceClient.unload()
        try? FileManager.default.removeItem(at: KokoroVoiceClient.modelDirectory)
        try? PulsarConfig.shared.set(PulsarConfig.voiceEngineKey, value: VoiceEngine.native.rawValue)
        phase = .notInstalled
    }

    /// Bytes on disk, for the Settings subtitle. nil when nothing is installed.
    func installedSize() -> Int64? {
        let dir = KokoroVoiceClient.modelDirectory
        guard let e = FileManager.default.enumerator(
            at: dir, includingPropertiesForKeys: [.fileSizeKey]) else { return nil }
        var total: Int64 = 0
        for case let url as URL in e {
            total += Int64((try? url.resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0)
        }
        return total > 0 ? total : nil
    }

    enum DownloadError: LocalizedError {
        case badURL(String)
        case http(Int, String)

        var errorDescription: String? {
            switch self {
            case .badURL(let s):      return "Bad download URL: \(s)"
            case .http(let c, let s): return "Download failed (HTTP \(c)): \(s)"
            }
        }
    }
}
