#!/usr/bin/env bash
# Fetch the prebuilt MLX Metal shader library that the Kokoro voice engine needs.
#
# WHY THIS EXISTS
# ---------------
# `swift build` CANNOT compile MLX's Metal kernels — mlx-swift's own README says so
# outright ("SwiftPM (command line) cannot build the Metal shaders, xcodebuild can").
# The failure mode is nasty: the build exits 0, ships no shader library, and MLX only
# dies at RUNTIME with "Failed to load the default metallib".
#
# Rather than move Pulsar's whole release pipeline to xcodebuild (which would mean a
# full Xcode install on every build machine), we fetch the shaders Apple's own MLX
# project already publishes precompiled, as the `mlx-metal` wheel on PyPI. It is a
# pure-data wheel — no Python is installed or run, we just unzip it.
#
# VERSION MATCHING IS LOAD-BEARING
# --------------------------------
# The metallib must match the MLX C++ version that mlx-swift vendors, or kernels go
# missing at runtime. mlx-swift 0.31.3 vendors MLX C++ 0.31.1 (see
# Source/Cmlx/mlx/mlx/version.h in the resolved checkout). If you bump the mlx-swift
# pin in Vendor/kokoro-swift/Package.swift, bump MLX_VERSION here to match.
#
# The macosx_14_0 build is chosen to match Pulsar's .macOS(.v14) deployment target.
set -euo pipefail

MLX_VERSION="${MLX_VERSION:-0.31.1}"
PLATFORM="${MLX_PLATFORM:-macosx_14_0_arm64}"
WHEEL="mlx_metal-${MLX_VERSION}-py3-none-${PLATFORM}.whl"

CACHE_DIR="${MLX_METALLIB_CACHE:-$HOME/Library/Caches/Pulsar/mlx-metallib}"
DEST="${1:-}"

if [[ -z "$DEST" ]]; then
  echo "usage: $(basename "$0") <destination-path-for-mlx.metallib>" >&2
  exit 64
fi

CACHED="$CACHE_DIR/${MLX_VERSION}-${PLATFORM}/mlx.metallib"

if [[ ! -f "$CACHED" ]]; then
  echo "Fetching MLX ${MLX_VERSION} Metal shaders (${PLATFORM})…"
  mkdir -p "$CACHE_DIR/${MLX_VERSION}-${PLATFORM}"
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT

  # Resolve the wheel URL from the PyPI JSON API rather than hardcoding a hash path,
  # so the script survives PyPI re-hosting the file.
  URL="$(curl -fsSL "https://pypi.org/pypi/mlx-metal/${MLX_VERSION}/json" \
    | python3 -c "
import json,sys
want = '${WHEEL}'
d = json.load(sys.stdin)
for f in d['urls']:
    if f['filename'] == want:
        print(f['url']); break
else:
    sys.exit('no wheel named ' + want)
")"

  curl -fsSL -o "$TMP/wheel.zip" "$URL"
  unzip -q -o "$TMP/wheel.zip" -d "$TMP/x"

  FOUND="$(find "$TMP/x" -name 'mlx.metallib' -print -quit)"
  if [[ -z "$FOUND" ]]; then
    echo "Error: no mlx.metallib inside $WHEEL" >&2
    exit 1
  fi
  mv "$FOUND" "$CACHED"
  echo "Cached $(du -h "$CACHED" | cut -f1) → $CACHED"
fi

mkdir -p "$(dirname "$DEST")"
cp "$CACHED" "$DEST"
echo "mlx.metallib → $DEST"
