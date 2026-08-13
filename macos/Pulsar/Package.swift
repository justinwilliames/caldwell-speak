// swift-tools-version: 6.1
import PackageDescription
import Foundation

let packageDir = URL(fileURLWithPath: #filePath).deletingLastPathComponent().path

let package = Package(
    name: "Pulsar",
    platforms: [.macOS(.v14)],
    dependencies: [
        // Hummingbird — SSWG-endorsed lightweight HTTP server. Used to host
        // the local API (/speak, /queue, /cache, /settings, /events, …)
        // inside the app process so we can retire the standalone Python
        // daemon. Keeping the HTTP surface preserves say.sh + Stop hook
        // compatibility while collapsing to a single binary.
        .package(url: "https://github.com/hummingbird-project/hummingbird.git", from: "2.0.0"),
        // Sparkle — in-app auto-update. Re-added after the 0.2.0 removal:
        // the prior attempt dyld-crashed because the framework was linked
        // but never embedded at Contents/Frameworks with a matching rpath.
        // build-pulsar-app.sh + package-dmg.yml now embed + sign it, and
        // the -rpath linker flag below bakes @executable_path/../Frameworks
        // into the binary so dyld resolves the embedded framework.
        .package(url: "https://github.com/sparkle-project/Sparkle", from: "2.6.0"),
        // Kokoro-82M on-device TTS (Apache-2.0), the OPT-IN second voice engine.
        // Vendored under Vendor/ rather than fetched by URL — see that package's
        // Package.swift for why. Pulls mlx-swift transitively; note that
        // `swift build` CANNOT compile MLX's Metal shaders, so the build script
        // fetches a matching prebuilt mlx.metallib (scripts/fetch-mlx-metallib.sh)
        // and places it beside the binary. Without it MLX fails at RUNTIME while
        // the build still exits 0.
        .package(path: "Vendor/kokoro-swift"),
        // Direct (not just transitive-via-Kokoro) so KokoroVoiceClient can import
        // MLX and BOUND ITS MEMORY. MLX's memoryLimit defaults to 1.5x the device's
        // max recommended working set — multiple GB on a unified-memory Mac — which
        // let a burst of syntheses swap the machine out from under itself
        // (13.7GB of 15.4GB swap, observed 13 Aug 2026). Must stay pin-compatible
        // with the exact version Vendor/kokoro-swift requires.
        .package(url: "https://github.com/ml-explore/mlx-swift.git", exact: "0.31.3"),
    ],
    targets: [
        .executableTarget(
            name: "Pulsar",
            dependencies: [
                .product(name: "Hummingbird", package: "hummingbird"),
                .product(name: "Sparkle", package: "Sparkle"),
                // Package identity for a path dependency is the DIRECTORY name
                // ("kokoro-swift"), not the `Package(name:)` inside it ("Kokoro").
                .product(name: "Kokoro", package: "kokoro-swift"),
                .product(name: "MLX", package: "mlx-swift"),
            ],
            path: "Sources",
            resources: [
                .copy("Resources/AppIcon.icns"),
                // OrbitLogo images — copied as plain PNGs to the resource bundle,
                // then explicitly placed in Contents/Resources/ by build-pulsar-app.sh
                // so Bundle.main can find them via NSImage(named:).
                .copy("Resources/OrbitLogo.png"),
                .copy("Resources/OrbitLogo@2x.png"),
                .copy("Resources/OrbitLogo@3x.png"),
                // Pulsar mouth sprites — 5 rendered frames of one robot, mouth
                // closed (0) → full open (4). PortraitView crossfades adjacent
                // frames by amplitude. Placed in Contents/Resources/ by the
                // build script so Bundle.main finds them via NSImage(named:).
                .copy("Resources/pulsar-mouth-0.png"),
                .copy("Resources/pulsar-mouth-1.png"),
                .copy("Resources/pulsar-mouth-2.png"),
                .copy("Resources/pulsar-mouth-3.png"),
                .copy("Resources/pulsar-mouth-4.png"),
                // Blink frame — same robot, eyes closed (eyebrows kept). Briefly
                // crossfaded over the closed mouth frame during speech pauses.
                .copy("Resources/pulsar-blink.png"),
                // Sub-agent drone frames — 6 sibling robots (voyager/sentinel/
                // nova/nebula/echo/atlas), each 5 mouth frames (0 closed → 4 open)
                // + a blink, same scheme as Pulsar. PortraitView loads them per drone.
                .copy("Resources/voyager-mouth-0.png"),
                .copy("Resources/voyager-mouth-1.png"),
                .copy("Resources/voyager-mouth-2.png"),
                .copy("Resources/voyager-mouth-3.png"),
                .copy("Resources/voyager-mouth-4.png"),
                .copy("Resources/voyager-blink.png"),
                .copy("Resources/sentinel-mouth-0.png"),
                .copy("Resources/sentinel-mouth-1.png"),
                .copy("Resources/sentinel-mouth-2.png"),
                .copy("Resources/sentinel-mouth-3.png"),
                .copy("Resources/sentinel-mouth-4.png"),
                .copy("Resources/sentinel-blink.png"),
                .copy("Resources/nova-mouth-0.png"),
                .copy("Resources/nova-mouth-1.png"),
                .copy("Resources/nova-mouth-2.png"),
                .copy("Resources/nova-mouth-3.png"),
                .copy("Resources/nova-mouth-4.png"),
                .copy("Resources/nova-blink.png"),
                .copy("Resources/nebula-mouth-0.png"),
                .copy("Resources/nebula-mouth-1.png"),
                .copy("Resources/nebula-mouth-2.png"),
                .copy("Resources/nebula-mouth-3.png"),
                .copy("Resources/nebula-mouth-4.png"),
                .copy("Resources/nebula-blink.png"),
                .copy("Resources/echo-mouth-0.png"),
                .copy("Resources/echo-mouth-1.png"),
                .copy("Resources/echo-mouth-2.png"),
                .copy("Resources/echo-mouth-3.png"),
                .copy("Resources/echo-mouth-4.png"),
                .copy("Resources/echo-blink.png"),
                .copy("Resources/atlas-mouth-0.png"),
                .copy("Resources/atlas-mouth-1.png"),
                .copy("Resources/atlas-mouth-2.png"),
                .copy("Resources/atlas-mouth-3.png"),
                .copy("Resources/atlas-mouth-4.png"),
                .copy("Resources/atlas-blink.png"),
                .copy("Resources/iris-mouth-0.png"),
                .copy("Resources/iris-mouth-1.png"),
                .copy("Resources/iris-mouth-2.png"),
                .copy("Resources/iris-mouth-3.png"),
                .copy("Resources/iris-mouth-4.png"),
                .copy("Resources/iris-blink.png"),
                .copy("Resources/meridian-mouth-0.png"),
                .copy("Resources/meridian-mouth-1.png"),
                .copy("Resources/meridian-mouth-2.png"),
                .copy("Resources/meridian-mouth-3.png"),
                .copy("Resources/meridian-mouth-4.png"),
                .copy("Resources/meridian-blink.png"),
                // Claude Code voice-integration payload — the skill, the hooks,
                // say.sh + CANON.md + voices.json. Bundled verbatim so a DMG-only
                // user (no repo) can one-click install Pulsar's Claude integration
                // from inside the app. The whole directory is copied into the SPM
                // resource bundle, then build-pulsar-app.sh re-syncs it from the
                // repo (so it never goes stale) and lifts it into
                // Contents/Resources/claude-integration/ for ClaudeIntegrationInstaller.
                .copy("Resources/claude-integration"),
            ],
            swiftSettings: [
                .swiftLanguageMode(.v5),
            ],
            linkerSettings: [
                .unsafeFlags(["-Xlinker", "-sectcreate",
                              "-Xlinker", "__TEXT",
                              "-Xlinker", "__info_plist",
                              "-Xlinker", "\(packageDir)/Info.plist",
                              // Resolve the embedded Sparkle.framework at runtime
                              // from the .app bundle's Frameworks dir.
                              "-Xlinker", "-rpath",
                              "-Xlinker", "@executable_path/../Frameworks"])
            ]
        ),
    ]
)
