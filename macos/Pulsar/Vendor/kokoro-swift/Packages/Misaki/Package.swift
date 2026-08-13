// swift-tools-version: 6.0
//
// VENDORED — the Misaki G2P engine shipped inside mweinbach/kokoro-swift.
// This is what makes Kokoro viable here at all: it phonemises English in pure
// Swift, so there is NO espeak-ng dependency and therefore no GPL obligation on
// a repo that ships an MIT-licensed app.
//
// Trimmed from upstream: the test target is dropped (its directory is not
// vendored). Sources/ and Resources/ are unmodified.
import PackageDescription

let package = Package(
    name: "Misaki",
    platforms: [
        .macOS(.v14),
        .iOS(.v17),
    ],
    products: [
        .library(
            name: "Misaki",
            targets: ["Misaki"]
        ),
    ],
    targets: [
        .target(
            name: "Misaki",
            resources: [
                .process("Resources"),
            ]
        ),
    ]
)
