#!/bin/sh
# build-pulsar-app.sh — compile the SwiftUI menu-bar app and assemble
# a proper Pulsar.app bundle.
#
# Requires macOS 26 (Tahoe) — the app uses Liquid Glass APIs that don't
# exist on earlier macOS versions.
# Requires Swift 6.1+ — bundled with macOS 26.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_DIR="$REPO_ROOT/macos/Pulsar"
BUILD_DIR="$APP_DIR/build"
APP_BUNDLE="$BUILD_DIR/Pulsar.app"

# macOS version sanity check
MACOS_MAJOR="$(sw_vers -productVersion | cut -d. -f1)"
if [ "$MACOS_MAJOR" -lt 26 ]; then
  echo "Error: this app requires macOS 26 (Tahoe) or later." >&2
  echo "Current macOS: $(sw_vers -productVersion)" >&2
  echo "Use Plash or the web dashboard until you upgrade." >&2
  exit 1
fi

if ! command -v swift >/dev/null 2>&1; then
  echo "Error: swift not found. Install Xcode or Command Line Tools:" >&2
  echo "  xcode-select --install" >&2
  exit 1
fi

cd "$APP_DIR"

# Re-sync the Claude voice-integration payload from the repo's source-of-truth
# copies into the app's staging dir, so a stale Sources/Resources/claude-integration
# can never ship. These are the exact files the in-app installer drops into the
# user's ~/.claude. Keep this list in lockstep with ClaudeIntegrationInstaller.swift.
CLAUDE_STAGE="$APP_DIR/Sources/Resources/claude-integration"
echo "Syncing Claude integration payload into the app staging dir..."
mkdir -p "$CLAUDE_STAGE/scripts"
cp "$REPO_ROOT/SKILL.md"    "$CLAUDE_STAGE/SKILL.md"
cp "$REPO_ROOT/CANON.md"    "$CLAUDE_STAGE/CANON.md"
cp "$REPO_ROOT/voices.json" "$CLAUDE_STAGE/voices.json"
# pulsar-team skill (SKILL.md + scripts) — canonical at repo pulsar-team/;
# without this re-sync the embedded copy forks silently (found 2026-07-20:
# it had to be hand-copied on every edit).
mkdir -p "$CLAUDE_STAGE/skills/pulsar-team/scripts"
cp "$REPO_ROOT/pulsar-team/SKILL.md" "$CLAUDE_STAGE/skills/pulsar-team/SKILL.md"
cp "$REPO_ROOT/pulsar-team/scripts/"*.sh "$CLAUDE_STAGE/skills/pulsar-team/scripts/" 2>/dev/null || true
chmod +x "$CLAUDE_STAGE/skills/pulsar-team/scripts/"*.sh 2>/dev/null || true
for f in say.sh session-start-voice.sh stop-hook.sh chime.sh turn-start.sh statusline.sh subagent-start.sh subagent-stop.sh install-hooks.sh uninstall-hooks.sh; do
  cp "$REPO_ROOT/scripts/$f" "$CLAUDE_STAGE/scripts/$f"
done

echo "Building release binary (this can take a minute)..."
swift build -c release

BINARY="$APP_DIR/.build/release/Pulsar"
if [ ! -f "$BINARY" ]; then
  # Apple Silicon may put it under a triple-prefixed dir
  BINARY="$(find "$APP_DIR/.build" -name Pulsar -type f -path "*/release/*" 2>/dev/null | head -1)"
fi

if [ ! -f "$BINARY" ]; then
  echo "Error: build did not produce a Pulsar binary under .build/" >&2
  exit 1
fi

echo "Assembling Pulsar.app..."
rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
cp "$BINARY" "$APP_BUNDLE/Contents/MacOS/Pulsar"
cp "$APP_DIR/Info.plist" "$APP_BUNDLE/Contents/Info.plist"
printf 'APPL????' > "$APP_BUNDLE/Contents/PkgInfo"

# Bundle resources — the app icon (Info.plist sets CFBundleIconFile=AppIcon)
# and the portrait PNGs. CI's package-dmg.yml copies these; the local build
# previously skipped them, producing an icon-less /Applications bundle.
mkdir -p "$APP_BUNDLE/Contents/Resources"
cp "$APP_DIR/Sources/Resources/AppIcon.icns" "$APP_BUNDLE/Contents/Resources/AppIcon.icns"
if [ -d "$REPO_ROOT/assets/portraits" ]; then
  mkdir -p "$APP_BUNDLE/Contents/Resources/assets"
  cp -R "$REPO_ROOT/assets/portraits" "$APP_BUNDLE/Contents/Resources/assets/portraits"
fi

# Third-party notices. Sparkle's MIT licence and the Apache-2.0 grant on the
# SwiftNIO/Hummingbird tree both require their attribution text to travel with
# the distributed binary, so the notices ship inside the bundle rather than
# living only in the repo. Unguarded on purpose: a missing file fails the build
# instead of quietly shipping an app with no attribution.
cp "$REPO_ROOT/THIRD-PARTY-NOTICES.md" "$APP_BUNDLE/Contents/Resources/THIRD-PARTY-NOTICES.md"

# GUARD — every drone in the registry must have all six frame assets DECLARED in
# Package.swift, not merely present on disk. SPM cannot glob resources, so the list
# there is hand-written, and when the tenth drone was added every other stage of the
# pipeline picked it up while that list did not. The app built clean, installed clean,
# reported success, and shipped one drone that could not open its mouth. Fail loudly
# here instead.
REG="$REPO_ROOT/macos/Pulsar/Sources/Models/DroneRegistry.swift"
PKG="$REPO_ROOT/macos/Pulsar/Package.swift"
if [ -f "$REG" ] && [ -f "$PKG" ]; then
  missing=""
  for d in $(grep -oE 'Drone\(category: "[a-z]+"' "$REG" | sed 's/.*"\(.*\)"/\1/' | grep -v unknown); do
    for f in mouth-0 mouth-1 mouth-2 mouth-3 mouth-4 blink; do
      grep -q "Resources/$d-$f.png" "$PKG" || missing="$missing $d-$f"
    done
  done
  if [ -n "$missing" ]; then
    echo "ERROR: frame assets missing from Package.swift resources:$missing" >&2
    echo "       Add a .copy(\"Resources/<name>.png\") line for each, or the drone ships mute." >&2
    exit 1
  fi
  echo "Frame-asset guard: every registry drone has six declared assets."
fi

# OrbitLogo PNGs — copied by SPM into the build's resource bundle; extract
# them into Contents/Resources/ so Bundle.main can find them via NSImage(named:).
RESOURCE_BUNDLE="$(find "$APP_DIR/.build" -name "Pulsar_Pulsar.bundle" -path "*/release/*" 2>/dev/null | head -1)"
if [ -n "$RESOURCE_BUNDLE" ] && [ -d "$RESOURCE_BUNDLE" ]; then
  # Enumerate the frame assets by PATTERN, never by a hand-written list.
  #
  # This used to be an explicit list of nine characters x six frames. When the tenth
  # drone (vector) was added, every other part of the pipeline picked it up and this
  # list did not — so the app built clean, installed clean, reported success, and
  # shipped with 54 of 60 assets and one drone that could not open its mouth. A
  # hardcoded roster in a build script is a silent-failure generator; the glob cannot
  # miss a character nobody remembered to add.
  for f in $(cd "$RESOURCE_BUNDLE" 2>/dev/null && ls OrbitLogo*.png *-mouth-[0-4].png *-blink.png 2>/dev/null); do
    src="$RESOURCE_BUNDLE/$f"
    if [ -f "$src" ]; then
      cp "$src" "$APP_BUNDLE/Contents/Resources/$f"
    fi
  done
  echo "Copied OrbitLogo + pulsar-mouth + blink PNGs to Contents/Resources."

  # Claude voice-integration payload: SPM copies the whole directory verbatim
  # into the resource bundle. Lift it into Contents/Resources/claude-integration/
  # so ClaudeIntegrationInstaller can find it via Bundle.main.resourceURL. Keep
  # the scripts executable so the installed hooks run without a chmod dance.
  CI_SRC="$RESOURCE_BUNDLE/claude-integration"
  if [ -d "$CI_SRC" ]; then
    rm -rf "$APP_BUNDLE/Contents/Resources/claude-integration"
    cp -R "$CI_SRC" "$APP_BUNDLE/Contents/Resources/claude-integration"
    chmod +x "$APP_BUNDLE/Contents/Resources/claude-integration/scripts/"*.sh 2>/dev/null || true
    echo "Copied claude-integration payload (skill + hooks + say.sh) to Contents/Resources."
  else
    echo "Warning: claude-integration payload not found in SPM bundle — in-app installer will be unavailable." >&2
  fi
else
  echo "Warning: SPM resource bundle not found — OrbitLogo may not render." >&2
fi

# Misaki's G2P lexicon (us/gb gold+silver JSON) ships as its own SPM resource
# bundle. SwiftPM's generated Bundle.module only looks beside the main bundle
# (Pulsar.app/Misaki_Misaki.bundle — outside Contents/, which codesign rejects)
# or at the absolute .build path of the machine that compiled it. The installed
# app therefore phonemised through this checkout's .build tree for a week and
# fell silent the day a disk clean-up deleted it (2026-09-02): every line failed
# at synthesis, and a fresh launch crashed on its first word. Ship the bundle in
# Contents/Resources, where MisakiResources looks first. Fatal if absent: Kokoro
# is the only engine, so a missing lexicon is a mute app.
MISAKI_BUNDLE="$(find "$APP_DIR/.build" -name "Misaki_Misaki.bundle" -path "*/release/*" 2>/dev/null | head -1)"
if [ -z "$MISAKI_BUNDLE" ] || [ ! -d "$MISAKI_BUNDLE" ]; then
  echo "Error: Misaki_Misaki.bundle not found under .build — Kokoro cannot phonemise without it." >&2
  exit 1
fi
rm -rf "$APP_BUNDLE/Contents/Resources/Misaki_Misaki.bundle"
cp -R "$MISAKI_BUNDLE" "$APP_BUNDLE/Contents/Resources/Misaki_Misaki.bundle"
for f in us_gold us_silver gb_gold gb_silver; do
  if [ -z "$(find "$APP_BUNDLE/Contents/Resources/Misaki_Misaki.bundle" -name "$f.json" 2>/dev/null)" ]; then
    echo "Error: $f.json missing from the shipped Misaki bundle." >&2
    exit 1
  fi
done
echo "Copied Misaki lexicon bundle to Contents/Resources."

# Embed Sparkle.framework. The binary loads @rpath/Sparkle.framework/... and
# carries an @executable_path/../Frameworks rpath (set in Package.swift), so
# the framework must live at Contents/Frameworks. The 0.2.0 attempt linked
# Sparkle but skipped this embed step and crashed at dyld before drawing a
# pixel — keep this in lockstep with package-dmg.yml's identical block.
FRAMEWORK_SRC="$(dirname "$BINARY")/Sparkle.framework"
if [ ! -d "$FRAMEWORK_SRC" ]; then
  echo "Error: Sparkle.framework not found next to the binary ($FRAMEWORK_SRC)." >&2
  echo "Did 'swift build' resolve the Sparkle SPM dependency?" >&2
  exit 1
fi
mkdir -p "$APP_BUNDLE/Contents/Frameworks"
rm -rf "$APP_BUNDLE/Contents/Frameworks/Sparkle.framework"
# ditto preserves the framework's Versions/ symlink layout (cp -R mangles it).
ditto "$FRAMEWORK_SRC" "$APP_BUNDLE/Contents/Frameworks/Sparkle.framework"

# Embed MLX's Metal shader library, for the Kokoro voice engine.
#
# `swift build` cannot compile MLX's Metal kernels (mlx-swift's README states this
# outright), and the failure is silent: the build exits 0 and MLX only dies at
# runtime with "Failed to load the default metallib". So fetch the matching
# precompiled shaders and colocate them with the executable — MLX checks the
# binary's own directory FIRST (backend/metal/device.cpp), before any bundle path.
#
# Not fatal if it fails: Kokoro is the OPT-IN engine, and Pulsar still speaks via
# macOS `say` without it. Better to ship a working app with one engine than to
# fail the build over an optional one.
METALLIB_DEST="$APP_BUNDLE/Contents/MacOS/mlx.metallib"
# Absolute path: the script cd's to $APP_DIR above, so a $0-relative path breaks.
if "$SCRIPT_DIR/fetch-mlx-metallib.sh" "$METALLIB_DEST"; then
  echo "Kokoro engine: Metal shaders embedded ($(du -h "$METALLIB_DEST" | cut -f1))."
else
  echo "Warning: could not fetch mlx.metallib — the Kokoro voice engine will be" >&2
  echo "         unavailable in this build. macOS 'say' is unaffected." >&2
fi

# Ad-hoc sign, inside-out: the embedded framework first (--deep catches its
# nested XPC services + Updater.app + Autoupdate), then the whole app last so
# its signature seals the framework and resources. Ad-hoc (`--sign -`) is
# sufficient: Sparkle validates updates via the EdDSA signature
# (SUPublicEDKey), not a Developer ID.
codesign --force --deep --sign - "$APP_BUNDLE/Contents/Frameworks/Sparkle.framework"
codesign --force --deep --sign - "$APP_BUNDLE"

# Fail loudly on a broken signature — that is precisely the launch-time
# regression Sparkle introduced last time.
if ! codesign --verify --deep --strict "$APP_BUNDLE"; then
  echo "Error: codesign verification failed on $APP_BUNDLE" >&2
  exit 1
fi

echo ""
echo "Built: $APP_BUNDLE"
echo "To install:  $SCRIPT_DIR/install-pulsar-app.sh"
echo "To run now:  open '$APP_BUNDLE'"
echo "Build complete!"
