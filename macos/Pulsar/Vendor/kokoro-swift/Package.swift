// swift-tools-version: 5.10
//
// VENDORED — mweinbach/kokoro-swift @ 20bf04c ("Initial release", 2026-04-06),
// Apache-2.0. Copied into the repo rather than referenced by URL because upstream
// is a single-commit repository with no maintenance history; a release pipeline
// should not be able to break because someone else's GitHub repo moved.
//
// Trimmed from upstream: the KokoroCLI executable target and the test target are
// dropped (Pulsar links the library only). Nothing in Sources/ is modified — keep
// it that way, so a future upstream diff stays readable.
//
// Upstream README is kept alongside as README.upstream.md.
import PackageDescription

let package = Package(
    name: "Kokoro",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .library(name: "Kokoro", targets: ["Kokoro"]),
    ],
    dependencies: [
        .package(path: "Packages/Misaki"),
        // Pinned exactly by upstream. mlx-swift 0.31.3 vendors MLX C++ 0.31.1 —
        // the version the shipped mlx.metallib must match. See
        // scripts/fetch-mlx-metallib.sh; changing this pin means refetching it.
        .package(url: "https://github.com/ml-explore/mlx-swift.git", exact: "0.31.3"),
    ],
    targets: [
        .target(
            name: "Kokoro",
            dependencies: [
                .product(name: "Misaki", package: "Misaki"),
                .product(name: "MLX", package: "mlx-swift"),
                .product(name: "MLXFast", package: "mlx-swift"),
                .product(name: "MLXNN", package: "mlx-swift"),
            ]
        ),
    ]
)
