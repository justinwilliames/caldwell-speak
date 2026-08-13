import Foundation
import Kokoro
import MLX

/// On-device neural TTS via Kokoro-82M (Apache-2.0), running through MLX on the
/// Apple Silicon GPU. The OPT-IN second engine — `say` (NativeVoiceClient) stays
/// the default and the fallback, so a stock install never depends on this.
///
/// Why a second engine rather than a replacement (2026-08-13, Justin):
///   • the 9-drone cast is built from macOS voices that ship on every Mac
///     (DroneRegistry), including novelty voices Kokoro has no analogue for.
///     Replacing `say` would collapse the cast; running alongside keeps it.
///   • Kokoro needs ~350MB of weights the user must consciously download.
///     A voice assistant that can't speak until it finishes a download is a
///     broken voice assistant, so `say` carries every line until Kokoro is ready.
///
/// Threading — READ THIS BEFORE EDITING. `KPipeline.synthesize` is SYNCHRONOUS
/// and CPU/GPU-heavy (hundreds of ms). Calling it from a `Task.detached` parks a
/// cooperative-pool thread for the whole synth, which is the exact pool-exhaustion
/// stall NativeVoiceClient's `terminationHandler` comment documents. Every synth
/// therefore runs on `synthQueue`, a dedicated serial queue OFF the cooperative
/// pool, bridged back with a continuation. Serial is deliberate: one MLX pipeline,
/// one GPU stream, and Pulsar speaks one line at a time anyway.
enum KokoroVoiceClient {

    /// Kokoro's native output rate. Fixed by the model.
    static let sampleRate = 24_000

    /// Speech speed multiplier. Kokoro's `speed` is not word-per-minute; 1.0 is
    /// the model's natural pace and reads close to NativeVoiceClient's 168 wpm.
    static let defaultSpeed: Float = 1.0

    /// Kokoro voice per drone category — the cast re-mapped from macOS voices.
    ///
    /// Chosen to preserve each character's gender + register rather than to
    /// match the old timbre (Kokoro is all natural-human, so novelty voices like
    /// Fred/Junior/Ralph have no equivalent and are re-cast on persona instead):
    ///
    ///   pulsar   Daniel   (en-GB male)   → bm_daniel  — same name, same accent
    ///   voyager  Fred     (dry veteran)  → am_onyx    — deep, weathered
    ///   sentinel Karen    (smug analyst) → bf_alice   — crisp, clipped
    ///   nova     Samantha (deadpan)      → af_sarah   — flat, even
    ///   nebula   Moira    (eccentric)    → bf_emma    — warm, lilting
    ///   echo     Junior   (quick, young) → am_puck    — bright, playful
    ///   atlas    Rishi    (blunt)        → am_fenrir  — gruff, direct
    ///   iris     Tessa    (bright)       → af_heart   — the model's A-grade voice
    ///   meridian Ralph    (dry counsel)  → bm_george  — formal, measured
    ///
    /// Every id here MUST exist in `VoiceDownloader.availableVoices` or the
    /// download will 404 — `requiredVoices` is what the installer fetches.
    static let droneVoices: [String: String] = [
        "voyager":  "am_onyx",
        "sentinel": "bf_alice",
        "nova":     "af_sarah",
        "nebula":   "bf_emma",
        "echo":     "am_puck",
        "atlas":    "am_fenrir",
        "iris":     "af_heart",
        "meridian": "bm_george",
    ]

    /// Pulsar's own voice — British male, keeps the Daniel continuity.
    static let pulsarVoice = "bm_daniel"

    /// The voices the installer downloads. Pulsar + every drone, nothing else:
    /// all 54 would be ~14MB of dead weight for languages Pulsar never speaks.
    static var requiredVoices: [String] {
        ([pulsarVoice] + droneVoices.values).sorted()
    }

    /// The Kokoro voice for a line tagged with drone `category`.
    /// nil / "pulsar" / unknown → Pulsar's own voice, mirroring
    /// `NativeVoiceClient.voice(forAgent:)` so routing is identical on both engines.
    static func voice(forAgent category: String?) -> String {
        guard let c = category?.lowercased().trimmingCharacters(in: .whitespaces),
              !c.isEmpty, let v = droneVoices[c] else {
            return pulsarVoice
        }
        return v
    }

    /// Can this machine run Kokoro at all? MLX is Apple-Silicon-only, so on an
    /// Intel Mac the engine must be HIDDEN rather than merely disabled — offering a
    /// 315MB download that can never work is worse than not offering it.
    static var isSupported: Bool {
        #if arch(arm64)
        return true
        #else
        return false
        #endif
    }

    // MARK: - Model location

    /// Where the weights live. Deliberately NOT `VoiceDownloader.defaultCacheDirectory()`
    /// (`~/Library/Caches/Kokoro`): macOS purges Caches under disk pressure, which
    /// would silently un-install a 350MB model the user explicitly asked for and
    /// leave the engine set to `kokoro` with nothing behind it. Application Support
    /// is user data — it survives.
    static var modelDirectory: URL {
        PulsarConfig.shared.storageRoot.appendingPathComponent("kokoro", isDirectory: true)
    }

    /// `config.json` beside the weights. Not part of `ConvertedWeightsManifest`,
    /// which only names the model + voices dir.
    static var configURL: URL {
        modelDirectory.appendingPathComponent("config.json", isDirectory: false)
    }

    /// Is Kokoro usable right now? Weights + config + EVERY required voice on disk.
    /// Deliberately strict: a partial download (interrupted mid-fetch) must read as
    /// NOT installed, otherwise the first drone with a missing voice throws at speak
    /// time — the one moment where a failure is audible.
    ///
    /// The weights are size-checked, not just existence-checked: a truncated
    /// safetensors file exists happily and fails later, inside KModel.
    static func isInstalled() -> Bool {
        let fm = FileManager.default
        guard fm.fileExists(atPath: configURL.path) else { return false }
        let manifest = ConvertedWeightsManifest(directory: modelDirectory)
        guard let size = try? fm.attributesOfItem(atPath: manifest.modelURL.path)[.size] as? Int,
              size >= expectedWeightsBytes else { return false }
        return requiredVoices.allSatisfy {
            fm.fileExists(atPath: manifest.voicesDirectoryURL
                .appendingPathComponent("\($0).npy", isDirectory: false).path)
        }
    }

    /// Exact size of `kokoro-v1_0.safetensors` on the HuggingFace repo, measured
    /// 2026-08-13. Used only as a truncation floor — an exact-equality check would
    /// break the moment upstream reuploads, which is a worse failure than a
    /// slightly-loose guard.
    static let expectedWeightsBytes = 324_752_712

    // MARK: - Pipeline lifecycle

    /// One shared pipeline. Constructing it loads ~350MB of weights onto the GPU
    /// (seconds); rebuilding per line would make every utterance unusably slow.
    /// Guarded by `synthQueue`, so it is only ever touched from that serial queue.
    nonisolated(unsafe) private static var pipeline: KPipeline?

    /// Dedicated serial queue — see the threading note in the type doc.
    ///
    /// `utility`, deliberately NOT `userInitiated`: Pulsar is a background
    /// commentator, not a foreground task. A lower QoS tells the scheduler it may
    /// yield to whatever the user is actually doing, which matters when nine queued
    /// lines arrive at once and the machine has better things to do than render
    /// them all immediately.
    private static let synthQueue = DispatchQueue(
        label: "team.yourorbit.pulsar.kokoro-synth", qos: .utility)

    /// Enforced quiet period between syntheses.
    ///
    /// Pulsar speaks one line at a time, but nine `/speak` calls enqueue nine synth
    /// jobs at once, and back-to-back GPU work gave the allocator no chance to hand
    /// memory back before the next line grabbed more. Justin's call (13 Aug 2026):
    /// a slight delay before a drone speaks is fine if it buys stability. Playback
    /// of one line runs seconds long anyway, so this is almost never audible — the
    /// synth is still comfortably ahead of the speaker.
    nonisolated(unsafe) private static var lastSynthEnd: Date?

    /// Wait out the cooldown. MUST be called on `synthQueue`; blocking here is safe
    /// precisely because this queue is ours and off the cooperative pool.
    private static func awaitCooldownOnQueue() {
        let cooldown = TimeInterval(PulsarConfig.shared.kokoroCooldownMs) / 1000
        guard cooldown > 0, let last = lastSynthEnd else { return }
        let remaining = cooldown - Date().timeIntervalSince(last)
        if remaining > 0 { Thread.sleep(forTimeInterval: remaining) }
    }

    /// Build (or return) the shared pipeline. MUST be called on `synthQueue`.
    ///
    /// `enableDownload: false` on the VoiceLoader is deliberate — every fetch goes
    /// through KokoroModelManager so the UI can show progress and the user stays in
    /// control of a 310MB transfer. A lazy download firing mid-sentence would stall
    /// the queue behind a silent network call.
    private static func pipelineOnQueue() throws -> KPipeline {
        if let p = pipeline { return p }
        configureMemoryLimits()
        let manifest = ConvertedWeightsManifest(directory: modelDirectory)
        let model = try KModel(configURL: configURL, weightsURL: manifest.modelURL)
        let voices = VoiceLoader(baseDirectory: manifest.voicesDirectoryURL,
                                 enableDownload: false)
        let p = KPipeline(model: model, voices: voices, langCode: "en-us")
        pipeline = p
        NSLog("[Kokoro] pipeline warm — weights at \(modelDirectory.path)")
        return p
    }

    /// Bound MLX's appetite. THIS IS NOT OPTIONAL — read before changing.
    ///
    /// MLX's `memoryLimit` defaults to 1.5x the device's max recommended working
    /// set, which on a unified-memory Mac is many gigabytes, and its buffer cache
    /// is unbounded by default. Pulsar is a menu-bar app that speaks a sentence
    /// occasionally; it has no business behaving like a training run. Left at the
    /// defaults, a burst of nine queued lines drove the machine to 13.7GB of 15.4GB
    /// swap and hung the desktop (observed 13 Aug 2026, a nine-drone roll call).
    ///
    /// Kokoro-82M is ~315MB of weights and its activations for one short utterance
    /// are small, so 1.5GB is generous headroom, not a squeeze. The cache limit
    /// follows MLX's own iOS guidance, which notes that small caches (single-digit
    /// MB) usually perform as well as unconstrained ones.
    private static func configureMemoryLimits() {
        MLX.Memory.memoryLimit = 1_536 * 1024 * 1024   // 1.5 GB ceiling
        MLX.Memory.cacheLimit = 64 * 1024 * 1024       // 64 MB of buffer reuse
        NSLog("[Kokoro] memory bounded — limit 1536MB, cache 64MB")
    }

    /// Drop the loaded model. Called when the user switches back to `say`, deletes
    /// the download, or simply stops talking for a while — ~315MB of resident memory
    /// is not something a menu-bar app should hold indefinitely.
    static func unload() {
        synthQueue.async {
            guard pipeline != nil else { return }
            pipeline = nil
            MLX.Memory.clearCache()
            NSLog("[Kokoro] pipeline unloaded — memory released")
        }
    }

    /// How long the model stays resident after the last line. Long enough that a
    /// normal back-and-forth session never pays the reload, short enough that the
    /// memory comes back after a coffee. Reload from a warm page cache is <1s.
    private static let idleUnloadSeconds: TimeInterval = 180

    nonisolated(unsafe) private static var idleUnloadWork: DispatchWorkItem?

    /// (Re)arm the idle timer. MUST be called on `synthQueue`.
    private static func scheduleIdleUnloadOnQueue() {
        idleUnloadWork?.cancel()
        let work = DispatchWorkItem {
            guard pipeline != nil else { return }
            pipeline = nil
            MLX.Memory.clearCache()
            NSLog("[Kokoro] idle \(Int(idleUnloadSeconds))s — pipeline unloaded")
        }
        idleUnloadWork = work
        synthQueue.asyncAfter(deadline: .now() + idleUnloadSeconds, execute: work)
    }

    /// Load the model NOW rather than on the first spoken line. The first synth
    /// pays a multi-second weight-load; without this the user's first line after
    /// enabling Kokoro arrives late enough to feel broken.
    static func warm() {
        synthQueue.async {
            _ = try? pipelineOnQueue()
        }
    }

    // MARK: - Synthesis

    /// Synthesise `text` to a temp WAV and return its URL. Caller owns the file.
    /// Signature deliberately mirrors `NativeVoiceClient.synth` so `VoiceEngine`
    /// can swap the two without either side knowing.
    static func synth(text: String, agent: String? = nil,
                      speed: Float = defaultSpeed) async throws -> URL {
        let voice = voice(forAgent: agent)
        let gapMs = PulsarConfig.shared.kokoroSentenceGapMs
        let out = URL(fileURLWithPath: NSTemporaryDirectory())
            .appendingPathComponent("pulsar-kokoro-\(UUID().uuidString).wav")

        return try await withCheckedThrowingContinuation { cont in
            synthQueue.async {
                do {
                    awaitCooldownOnQueue()
                    let pipe = try pipelineOnQueue()
                    // Lead-in silence, same 150ms as the `say` path. Kokoro has no
                    // `[[slnc]]` speech command, so the pad is prepended to the
                    // samples instead — without it afplay's device warm-up clips
                    // the first phoneme, the bug NativeVoiceClient.synth documents.
                    var samples = [Float](repeating: 0, count: sampleRate * 150 / 1000)

                    let parts = gapMs > 0 ? sentences(in: text) : [text]
                    let gap = [Float](repeating: 0, count: sampleRate * gapMs / 1000)
                    for (i, part) in parts.enumerated() {
                        // One autoreleasepool per sentence. MLX allocates Metal
                        // buffers through Objective-C; on a plain DispatchQueue
                        // (no runloop draining a pool for us) those temporaries
                        // would otherwise accumulate across every sentence of every
                        // queued line.
                        try autoreleasepool {
                            let r = try pipe.synthesize(text: part, voice: voice, speed: speed)
                            samples += parts.count > 1 ? trimSilence(r.audio) : r.audio
                        }
                        if i < parts.count - 1 { samples += gap }
                    }

                    try AudioWriter.writeWAV(samples: samples, to: out, sampleRate: sampleRate)

                    // Hand the buffers back rather than holding them until the next
                    // line. Pulsar speaks in bursts with long gaps, so a warm cache
                    // buys little and costs resident memory the whole time.
                    MLX.Memory.clearCache()
                    lastSynthEnd = Date()
                    scheduleIdleUnloadOnQueue()

                    let peak = MLX.Memory.peakMemory / (1024 * 1024)
                    NSLog("[Kokoro] ✓ \(voice) \(parts.count) sentence(s) @ \(gapMs)ms, peak \(peak)MB → '\(text.prefix(50))'")
                    cont.resume(returning: out)
                } catch {
                    try? FileManager.default.removeItem(at: out)
                    cont.resume(throwing: error)
                }
            }
        }
    }

    // MARK: - Pacing

    /// Split on sentence-final punctuation, keeping the punctuation with its
    /// sentence (Kokoro's prosody needs it — a chunk ending in "." falls, one
    /// ending in "?" rises).
    ///
    /// Why split at all: Kokoro renders a whole string as ONE utterance, so a full
    /// stop mid-string gets almost no pause and multi-sentence lines run together.
    /// Rendering each sentence separately and inserting real silence is the only
    /// lever that changes the gap without also slowing the words (`speed` does both).
    ///
    /// Abbreviations ("e.g.", "Dr.") will over-split. Left deliberately naive: a
    /// spurious extra pause is a much cheaper failure than a mangled sentence, and
    /// Pulsar's lines are short, spoken, and rarely carry abbreviations.
    static func sentences(in text: String) -> [String] {
        var out: [String] = []
        var current = ""
        let chars = Array(text)
        var i = 0
        while i < chars.count {
            let c = chars[i]
            current.append(c)
            if c == "." || c == "!" || c == "?" {
                // Absorb any run of closing punctuation ("!?", ".\"") before breaking.
                while i + 1 < chars.count, "!?.\"')]".contains(chars[i + 1]) {
                    i += 1
                    current.append(chars[i])
                }
                let next = i + 1 < chars.count ? chars[i + 1] : " "
                if next.isWhitespace {
                    let t = current.trimmingCharacters(in: .whitespacesAndNewlines)
                    if !t.isEmpty { out.append(t) }
                    current = ""
                }
            }
            i += 1
        }
        let tail = current.trimmingCharacters(in: .whitespacesAndNewlines)
        if !tail.isEmpty { out.append(tail) }
        return out.isEmpty ? [text] : out
    }

    /// Strip leading/trailing near-silence from one rendered sentence.
    ///
    /// Each Kokoro utterance carries its own head/tail padding — roughly 1.2s of
    /// combined dead air per sentence boundary when chunks are simply concatenated,
    /// which is far too long and, worse, not adjustable. Trimming first makes the
    /// configured gap the ONLY thing that sets the pause.
    static func trimSilence(_ samples: [Float], threshold: Float = 0.004,
                            marginMs: Int = 25) -> [Float] {
        guard let first = samples.firstIndex(where: { abs($0) > threshold }),
              let last = samples.lastIndex(where: { abs($0) > threshold })
        else { return samples }
        let margin = sampleRate * marginMs / 1000
        let lo = max(0, first - margin)
        let hi = min(samples.count - 1, last + margin)
        return Array(samples[lo...hi])
    }
}
