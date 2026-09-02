#!/bin/sh
# verify-app-selfsufficiency.sh — prove an assembled Pulsar.app carries everything
# it needs to run on a machine with no source checkout.
#
# WHY THIS EXISTS
# ---------------
# On 2026-09-02 Pulsar went silent. The cause was not the app: SwiftPM's generated
# `Bundle.module` had been resolving the Misaki phoneme lexicon out of the developer's
# `macos/Pulsar/.build` tree, so the INSTALLED app was reading a build directory. A
# routine disk clean-up deleted it and every spoken line failed at synthesis, while a
# fresh launch crashed on its first word. The heads still animated, so it read as a
# mute bug for nine hours.
#
# Two sibling faults surfaced in the same audit: the /portraits route read assets from
# `~/code/pulsar`, and CI never embedded MLX's Metal shaders at all — so every
# published DMG installed and never spoke.
#
# The pattern is the problem: an app that quietly reads the machine that built it looks
# perfect on that machine, and only that machine. So assert it, every build.
#
# Usage: verify-app-selfsufficiency.sh [/path/to/Pulsar.app]   (default: /Applications)
set -eu

APP="${1:-/Applications/Pulsar.app}"
RES="$APP/Contents/Resources"
MACOS="$APP/Contents/MacOS"
fail=0

say_fail() { echo "  FAIL  $1" >&2; fail=1; }
say_pass() { echo "  ok    $1"; }

[ -d "$APP" ] || { echo "No app bundle at $APP" >&2; exit 1; }
echo "Auditing $APP"

# 1. Phoneme lexicon. Kokoro cannot turn text into sound without it, and its
#    absence is a fatalError on first synthesis, not a graceful failure.
if [ -d "$RES/Misaki_Misaki.bundle" ]; then
  missing=""
  for f in us_gold us_silver gb_gold gb_silver; do
    [ -n "$(find "$RES/Misaki_Misaki.bundle" -name "$f.json" 2>/dev/null)" ] || missing="$missing $f"
  done
  [ -z "$missing" ] && say_pass "Misaki lexicon (4 files)" \
    || say_fail "Misaki lexicon incomplete:$missing"
else
  say_fail "Misaki_Misaki.bundle absent — every spoken line will fail at synthesis"
fi

# 2. MLX Metal shaders. `swift build` cannot compile them and says nothing.
if [ -f "$MACOS/mlx.metallib" ]; then
  say_pass "mlx.metallib ($(du -h "$MACOS/mlx.metallib" | cut -f1))"
else
  say_fail "mlx.metallib absent — MLX dies at first synthesis and there is no fallback engine"
fi

# 3. Faces. Every drone in the registry needs five mouth frames and a blink,
#    loaded by name from the bundle.
REG="$(dirname "$0")/../macos/Pulsar/Sources/Models/DroneRegistry.swift"
if [ -f "$REG" ]; then
  missing=""
  for d in $(grep -oE 'Drone\(category: "[a-z]+"' "$REG" | sed 's/.*"\(.*\)"/\1/' | grep -v unknown); do
    for f in mouth-0 mouth-1 mouth-2 mouth-3 mouth-4 blink; do
      [ -f "$RES/$d-$f.png" ] || missing="$missing $d-$f"
    done
  done
  [ -z "$missing" ] && say_pass "drone face frames" || say_fail "face frames absent:$missing"
else
  echo "  skip  face frames (registry not readable from here)"
fi

# 4. The Claude integration payload the in-app installer copies into ~/.claude.
[ -f "$RES/claude-integration/scripts/say.sh" ] \
  && say_pass "claude-integration payload" \
  || say_fail "claude-integration payload absent — the in-app installer has nothing to install"

# 5. Sparkle, which the binary loads via @rpath at launch.
[ -d "$APP/Contents/Frameworks/Sparkle.framework" ] \
  && say_pass "Sparkle.framework embedded" \
  || say_fail "Sparkle.framework absent — dyld will fail before the app draws a pixel"

# 6. THE ACTUAL RULE: no runtime path may point at a source checkout. Debug info
#    inside the compiled MLX objects legitimately carries .build paths, so this
#    looks only at the Swift string literals the app can actually open.
leaks="$(strings -a "$MACOS/Pulsar" 2>/dev/null \
  | grep -E '^/Users/[^/]+/(code|Developer|src)/' \
  | grep -vE '\.(h|hpp|cpp|c|swift)$' | sort -u || true)"
if [ -n "$leaks" ]; then
  say_fail "runtime paths pointing at a source checkout:"
  echo "$leaks" | sed 's/^/          /' >&2
else
  say_pass "no runtime path escapes the bundle"
fi

# 7. Signature. An unsealed bundle is refused at launch by launchd constraints.
codesign --verify --deep --strict "$APP" 2>/dev/null \
  && say_pass "signature verifies" \
  || say_fail "codesign verification failed"

echo
if [ "$fail" -eq 0 ]; then
  echo "Self-sufficient: this bundle needs nothing outside itself."
else
  echo "NOT self-sufficient — see failures above." >&2
fi
exit "$fail"
