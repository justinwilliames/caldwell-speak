import Foundation

/// Where Misaki's lexicon JSON lives at runtime.
///
/// SwiftPM's generated `Bundle.module` looks in exactly two places: beside the
/// main bundle (`Pulsar.app/Misaki_Misaki.bundle` — outside `Contents/`, which a
/// sealed app bundle cannot carry) and the absolute `.build/…` path of the
/// machine that compiled it. Neither exists for an installed app, so the
/// accessor `fatalError`s on first use — and first use is the first synthesis
/// after a pipeline (re)build, not launch. Pulsar ran for a week on that second
/// path until a disk clean-up deleted `.build`; from then on every line failed,
/// and a fresh launch crashed on its first word (2026-09-02).
///
/// Resolution order:
///   1. `Contents/Resources/Misaki_Misaki.bundle` — where the app build script
///      places it.
///   2. `Bundle.module` — only outside an installed `.app` (tests, `swift run`),
///      where the generated accessor's build-tree candidate can exist. Inside an
///      app with no bundle this returns nil and the lexicon load THROWS, which is
///      a logged, failed line rather than a crash loop.
enum MisakiResources {
    static let bundleName = "Misaki_Misaki.bundle"

    nonisolated(unsafe) private static let resolved: Bundle? = {
        if let resourceURL = Bundle.main.resourceURL,
           let bundle = Bundle(url: resourceURL.appendingPathComponent(bundleName, isDirectory: true)) {
            return bundle
        }
        if Bundle.main.bundleURL.pathExtension == "app" {
            return nil
        }
        return Bundle.module
    }()

    static func url(forResource name: String, withExtension ext: String) -> URL? {
        resolved?.url(forResource: name, withExtension: ext)
    }
}
