import Foundation

/// Where Misaki's lexicon JSON lives at runtime.
///
/// SwiftPM's generated `Bundle.module` looks in exactly two places: beside the
/// main bundle (`Pulsar.app/Misaki_Misaki.bundle` — outside `Contents/`, which a
/// sealed app bundle cannot carry) and the absolute `.build/…` path of the machine
/// that compiled it. Neither exists for an installed app, so the accessor
/// `fatalError`s on first use — and first use is the first synthesis after a
/// pipeline (re)build, not launch. Pulsar ran for a week on that second path until
/// a disk clean-up deleted `.build`; from then every line failed, and a fresh
/// launch crashed on its first word (2026-09-02).
///
/// `Bundle.module` is deliberately NOT referenced here, even as a fallback. Naming
/// it compiles that machine-specific path into the shipped binary, and a path an
/// installed app can reach is a path it will eventually read. The two locations
/// below are both relative to the running executable, so they are correct on any
/// machine:
///
///   1. `Contents/Resources/` — an installed `.app`, where the build script puts it.
///   2. Beside the executable — `swift run` / `swift test`, where SwiftPM puts it.
///
/// Finding neither returns nil, and the lexicon load throws: a logged, failed line
/// rather than a crash loop.
enum MisakiResources {
    static let bundleName = "Misaki_Misaki.bundle"

    nonisolated(unsafe) private static let resolved: Bundle? = {
        var candidates: [URL] = []
        if let resources = Bundle.main.resourceURL {
            candidates.append(resources.appendingPathComponent(bundleName, isDirectory: true))
        }
        // The executable's own directory, for non-.app contexts (tests, swift run).
        let executableDir = Bundle.main.executableURL?.deletingLastPathComponent()
        if let executableDir {
            candidates.append(executableDir.appendingPathComponent(bundleName, isDirectory: true))
        }
        for url in candidates where FileManager.default.fileExists(atPath: url.path) {
            if let bundle = Bundle(url: url) { return bundle }
        }
        return nil
    }()

    static func url(forResource name: String, withExtension ext: String) -> URL? {
        resolved?.url(forResource: name, withExtension: ext)
    }
}
