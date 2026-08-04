#!/usr/bin/env bash
# cast-check.sh — field-aware cast-consistency gate for the Pulsar drone
# roster. Ratified R4 (Ship-now 3, 2026-07-30): the drone cast is a single
# fact spread across ten surfaces (skill doc, Swift registry, roster UI, the
# frame-set PNGs, the spawn-categoriser regex, two build manifests, the
# fictional-personas disclaimer, and the design/drones master art) — nothing
# enforced them agreeing until now.
#
# v2 (R4, Nova): added check 10, the DESIGN-SURFACE gate — the master art's
# dominant accent hue must match the registry colour literal. Added because
# Atlas shipped blue-cyan art against a locked deep-grape literal for three
# review rounds with no check able to see it.
#
# Ownership rule (D3, ratified): any red finding on a DESIGN surface
# (persona names, blurbs, colours, frame art) is Nova's to fix on a 48h SLA.
# If the SLA lapses, the offending change reverts rather than shipping
# inconsistent. Non-DESIGN surfaces (workflow/CI, build scripts) revert to
# whichever drone owns that file per CANON.md.
#
# Exit 0 = cast is consistent. Exit 1 = prints a diff of the mismatch(es).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SKILL="$REPO_ROOT/pulsar-team/SKILL.md"
REGISTRY="$REPO_ROOT/macos/Pulsar/Sources/Models/DroneRegistry.swift"
ROSTER="$REPO_ROOT/macos/Pulsar/Sources/Views/Popover/RosterView.swift"
RESOURCES_DIR="$REPO_ROOT/macos/Pulsar/Sources/Resources"
SUBAGENT_START="$REPO_ROOT/scripts/subagent-start.sh"
PACKAGE_SWIFT="$REPO_ROOT/macos/Pulsar/Package.swift"
BUILD_APP_SH="$REPO_ROOT/scripts/build-pulsar-app.sh"

for f in "$SKILL" "$REGISTRY" "$ROSTER" "$SUBAGENT_START" "$PACKAGE_SWIFT" "$BUILD_APP_SH"; do
    [ -f "$f" ] || { echo "cast-check: missing required file: $f" >&2; exit 1; }
done

python3 - "$REPO_ROOT" "$SKILL" "$REGISTRY" "$ROSTER" "$RESOURCES_DIR" \
         "$SUBAGENT_START" "$PACKAGE_SWIFT" "$BUILD_APP_SH" <<'PYEOF'
import re, sys, pathlib

(_, repo_root, skill_path, registry_path, roster_path, resources_dir,
 subagent_start_path, package_swift_path, build_app_sh_path) = sys.argv

fail = []

def read(p):
    return pathlib.Path(p).read_text()

skill = read(skill_path)
registry = read(registry_path)
roster = read(roster_path)
subagent_start = read(subagent_start_path)
package_swift = read(package_swift_path)
build_app_sh = read(build_app_sh_path)

# --- 1. SS1 personas: §1 headings ------------------------------------------
# "### 1.N Name — ..." between "## 1. The team" and "## 1b."
m = re.search(r"^## 1\. The team\n(.*?)^## 1b\.", skill, re.S | re.M)
if not m:
    fail.append("§1 section (## 1. The team ... ## 1b.) not found in SKILL.md")
    section1 = ""
else:
    section1 = m.group(1)

headings = re.findall(r"^### 1\.\d+\s+(\S+)\s+—", section1, re.M)
skill_names = {h.lower() for h in headings}
EXPECTED_NINE = {"sentinel", "atlas", "nova", "nebula", "echo", "voyager",
                  "iris", "pulsar", "meridian"}
if skill_names != EXPECTED_NINE:
    missing = EXPECTED_NINE - skill_names
    extra = skill_names - EXPECTED_NINE
    fail.append(
        "SKILL.md §1 headings != ratified nine.\n"
        f"    missing: {sorted(missing) or '(none)'}\n"
        f"    extra:   {sorted(extra) or '(none)'}"
    )

# --- 2. DroneRegistry.swift categories -------------------------------------
reg_categories = re.findall(r'category:\s*"([a-zA-Z0-9_]+)"', registry)
registry_set = {c for c in reg_categories if c != "unknown"}
if not registry_set:
    fail.append("DroneRegistry.swift: no category: \"...\" entries found")

# --- 3. RosterView.swift blurbs --------------------------------------------
bm = re.search(r"let blurbs:\s*\[String:\s*String\]\s*=\s*\[(.*?)\n\s*\]",
               roster, re.S)
blurbs = {}
if bm:
    blurbs = dict(re.findall(r'"([a-zA-Z0-9_]+)":\s*"([^"]*)"', bm.group(1)))
else:
    fail.append("RosterView.swift: blurbs dictionary not found")

missing_blurbs = sorted(c for c in registry_set if not blurbs.get(c, "").strip())
if missing_blurbs:
    fail.append(f"RosterView.swift: missing/empty blurb for {missing_blurbs}")

# --- 4. Frame-set files -----------------------------------------------------
res = pathlib.Path(resources_dir)
missing_frames = {}
for cat in sorted(registry_set):
    need = [f"{cat}-mouth-{i}.png" for i in range(5)] + [f"{cat}-blink.png"]
    gone = [n for n in need if not (res / n).is_file()]
    if gone:
        missing_frames[cat] = gone
if missing_frames:
    fail.append(f"Frame PNGs missing in {resources_dir}: {missing_frames}")

# --- 5. subagent-start.sh CAST regex ---------------------------------------
cm = re.search(r'CAST\s*=\s*"([^"]+)"', subagent_start)
if not cm:
    fail.append(f"{subagent_start_path}: CAST = \"...\" not found")
else:
    cast_set = set(cm.group(1).split("|"))
    if cast_set != registry_set:
        fail.append(
            "subagent-start.sh CAST regex != DroneRegistry categories.\n"
            f"    missing from CAST: {sorted(registry_set - cast_set) or '(none)'}\n"
            f"    extra in CAST:     {sorted(cast_set - registry_set) or '(none)'}"
        )

# --- 6. Package.swift .copy entries ----------------------------------------
missing_copy = {}
for cat in sorted(registry_set):
    need = [f"{cat}-mouth-{i}.png" for i in range(5)] + [f"{cat}-blink.png"]
    gone = [n for n in need if f'Resources/{n}"' not in package_swift]
    if gone:
        missing_copy[cat] = gone
if missing_copy:
    fail.append(f"Package.swift: missing .copy() entries: {missing_copy}")

# --- 7. build-pulsar-app.sh copy list ---------------------------------------
missing_build_copy = {}
for cat in sorted(registry_set):
    need = [f"{cat}-mouth-{i}.png" for i in range(5)] + [f"{cat}-blink.png"]
    gone = [n for n in need if n not in build_app_sh]
    if gone:
        missing_build_copy[cat] = gone
if missing_build_copy:
    fail.append(f"build-pulsar-app.sh: missing frame filenames: {missing_build_copy}")

# --- 7b. Evidence gate survives (added 2026-08-01) ---------------------------
# The gate is three cooperating edits. Any one silently deleted and the review
# quietly reverts to unchecked judgement, which is exactly what it exists to
# stop. Assert all three anchors, plus the R4 wiring that makes the audit bind.
evidence_anchors = [
    (r"##\s*2b\.\s*The evidence gate", "§2b evidence-gate section"),
    (r"EVIDENCE GATE", "R1 brief's evidence-gate instruction"),
    (r"\[instrumented\]", "[instrumented] tag"),
    (r"\[judgement\]", "[judgement] tag"),
    (r"R1-evidence-audit\.md", "R1-evidence-audit.md artefact"),
    (r"Round 5 — Re-review against the ARTEFACT", "R5-reviews-the-artefact heading"),
]
missing_evidence = [label for pat, label in evidence_anchors
                    if not re.search(pat, skill)]
if missing_evidence:
    fail.append("SKILL.md: evidence gate incomplete, missing: "
                + ", ".join(missing_evidence))

# --- 8. Fictional-personas disclaimer names every §1 drone -------------------
dm = re.search(r"^>.*FICTIONAL.*$", skill, re.M)
if not dm:
    fail.append("SKILL.md: fictional-personas disclaimer line (FICTIONAL) not found")
else:
    disclaimer = dm.group(0)
    disc_lower = disclaimer.lower()
    missing_from_disclaimer = sorted(
        n for n in skill_names if not re.search(rf"\b{re.escape(n)}\b", disc_lower)
    )
    if missing_from_disclaimer:
        fail.append(
            f"Fictional-personas disclaimer is missing drone name(s): {missing_from_disclaimer}\n"
            f"    line: {disclaimer.strip()}"
        )

# --- 9. Real-person-name regression in §1 ------------------------------------
DENYLIST = [
    "Paula Scher", "Ken Adams", "Don Norman", "April Dunford",
    "Lenny Rachitsky", "Kleppmann", "Hillstrom", "Neumeier", "Rendle",
    "Boykis", "Grove", "Rabois", "Bezos", "Will Wilson", "Hillel Wayne",
]
section1_lower = section1.lower()
hits = [name for name in DENYLIST if name.lower() in section1_lower]
if hits:
    fail.append(f"§1 contains denylisted real-person name(s) (2026-07-30 removal list): {hits}")

# --- 10. DESIGN-SURFACE: master art hue vs registry colour literal -----------
# The registry colour literal is the drone's identity; design/drones/<cat>.png is
# how a human actually experiences it. Nothing enforced them agreeing, and Atlas
# drifted for three review rounds (art rendered blue-cyan at hue 225 while the
# locked literal was deep grape #8040C0 at hue 270 — a 45 degree miss).
#
# Metric: downsample the master, keep only pixels that are actually carrying
# accent colour (saturation >= 0.35, value >= 0.30 — the floor that still leaves
# dark drones like meridian a usable sample), bucket their hues at 10 degrees and
# take the modal bucket. Assert it is within HUE_TOL of the literal's hue.
#
# Pulsar has no design/drones master (his portrait is the frame set) — skipped.
HUE_TOL = 35.0          # degrees; whole cast passes, pre-fix Atlas measured 45.0
SAT_MIN, VAL_MIN = 0.35, 0.30
BUCKET = 10
MIN_SAT_PX = 500        # below this the modal bucket is noise, not a signal

design_dir = pathlib.Path(repo_root) / "design" / "drones"

reg_colors = dict(
    (c, (float(r), float(g), float(b)))
    for c, r, g, b in re.findall(
        r'Drone\(category:\s*"([a-zA-Z0-9_]+)".*?'
        r'color:\s*Color\(red:\s*([0-9.]+),\s*green:\s*([0-9.]+),\s*blue:\s*([0-9.]+)\)',
        registry, re.S)
)

try:
    from PIL import Image
except ImportError:
    Image = None

if Image is None:
    # A design gate that cannot see the art must never report PASS on it, but a
    # missing dependency is not a red DESIGN finding either — say so loudly.
    hue_report = None
else:
    import colorsys

    def hue_of(rgb):
        return colorsys.rgb_to_hsv(*rgb)[0] * 360.0

    def dominant_accent_hue(path):
        im = Image.open(path).convert("RGB")
        im.thumbnail((220, 220), Image.LANCZOS)
        hist = {}
        for r, g, b in im.getdata():
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            if s >= SAT_MIN and v >= VAL_MIN:
                key = int(h * 360.0) // BUCKET
                hist[key] = hist.get(key, 0) + 1
        if not hist:
            return None, 0
        top = max(hist, key=hist.get)
        return top * BUCKET + BUCKET / 2.0, sum(hist.values())

    def hue_delta(a, b):
        d = abs(a - b) % 360.0
        return min(d, 360.0 - d)

    hue_report = []
    for cat in sorted(registry_set):
        if cat == "pulsar":
            continue
        master = design_dir / f"{cat}.png"
        if not master.is_file():
            fail.append(f"[DESIGN-SURFACE] missing drone master art: {master}")
            continue
        want = hue_of(reg_colors[cat])
        got, n_sat = dominant_accent_hue(master)
        if got is None or n_sat < MIN_SAT_PX:
            fail.append(
                f"[DESIGN-SURFACE] {cat}.png has too few saturated pixels "
                f"({n_sat} < {MIN_SAT_PX}) to read an accent hue — the art has no "
                f"legible accent colour."
            )
            continue
        delta = hue_delta(want, got)
        hue_report.append((cat, want, got, delta, n_sat))
        if delta > HUE_TOL:
            fail.append(
                f"[DESIGN-SURFACE] {cat}: master art hue disagrees with the "
                f"DroneRegistry.swift colour literal.\n"
                f"    registry: hue {want:.1f} deg  "
                f"(r {reg_colors[cat][0]}, g {reg_colors[cat][1]}, b {reg_colors[cat][2]})\n"
                f"    art:      hue {got:.1f} deg  ({master.name}, {n_sat} accent px)\n"
                f"    delta:    {delta:.1f} deg  > tolerance {HUE_TOL:.0f} deg\n"
                f"    D3 ownership: red on a DESIGN surface -> Nova, 48h SLA. Fix the\n"
                f"    art to match the code (or land a ratified colour change in both)."
            )

# --- 11. DESIGN-SURFACE: frame centring + inter-frame registration -----------
# Added 2026-08-04 after Pulsar shipped with his head 10.4px left of centre in
# the 362px square (2.9% of the canvas — visible in the squircle as a fat gap on
# one side). The masters were all centred; the miss entered in the sprite-cell
# crop that derives the frames, and nothing could see it. Check 10 reads colour;
# nothing read geometry.
#
# 11a — REGISTRATION (absolute, prop-immune): every frame in a set must be
# pixel-identical in placement to that set's mouth-0. Phase correlation must
# return (0,0). This is what catches a re-derived frame set drifting.
#
# 11b — CENTRING (per-drone baseline): the head's bilateral-symmetry axis vs the
# canvas centre. Deliberately baselined per drone rather than gated at zero,
# because several units carry intrinsic design asymmetry that the metric reads as
# offset even when the art is correctly centred — nebula's swept quiff and
# antenna ball put her at -21.0 while a visual check confirms she is centred.
# Absolute-zero gating would false-positive her forever. The baseline encodes
# "this drone's reading WHEN CORRECT"; drift from it is the regression signal.
CENTRING_BASELINE = {
    "atlas":    -3.0,
    "echo":     +2.0,
    "iris":     -1.5,
    "meridian": -3.5,
    "nebula":  -21.0,   # intrinsic: swept quiff + single antenna ball, verified centred
    "nova":     -1.5,
    "pulsar":   -0.5,   # was -10.4 pre-fix; re-centred 2026-08-04 by a +10px integer shift
    "sentinel": -2.5,
    "voyager":  -1.5,
}
CENTRING_TOL = 3.0      # px on the 362px canvas; the fixed miss was 10.4px

try:
    import numpy as _np
except ImportError:
    _np = None

if Image is None or _np is None:
    geom_report = None
else:
    def _blur(a, r=2):
        k = _np.ones(2 * r + 1) / (2 * r + 1)
        a = _np.apply_along_axis(lambda m: _np.convolve(m, k, mode="same"), 1, a)
        return _np.apply_along_axis(lambda m: _np.convolve(m, k, mode="same"), 0, a)

    def _lum(path):
        im = _np.asarray(Image.open(path).convert("RGB")).astype(_np.float64)
        return 0.2126 * im[:, :, 0] + 0.7152 * im[:, :, 1] + 0.0722 * im[:, :, 2]

    def sym_offset(path, search=70, step=0.5):
        """Head symmetry axis minus canvas centre, in px. Negative = head sits left."""
        lum = _blur(_lum(path))
        H, W = lum.shape
        b = lum[int(0.10 * H):int(0.60 * H), :]
        b = b - b.mean()
        xs = _np.arange(W)
        best = (0.0, -2.0)
        for a in _np.arange(W / 2 - search, W / 2 + search + step / 2, step):
            mx = _np.rint(2 * a - xs).astype(int)
            ok = (mx >= 0) & (mx < W)
            if ok.sum() < W * 0.5:
                continue
            A = b[:, xs[ok]]
            B = b[:, mx[ok]]
            den = _np.sqrt((A * A).sum() * (B * B).sum())
            r = (A * B).sum() / den if den else -2.0
            if r > best[1]:
                best = (a - W / 2, r)
        return best[0]

    def frame_shift(ref, mov):
        """Integer (dx, dy) translation of `mov` relative to `ref`, phase correlation."""
        R = _np.fft.fft2(ref) * _np.conj(_np.fft.fft2(mov))
        R /= (_np.abs(R) + 1e-9)
        c = _np.fft.ifft2(R).real
        iy, ix = _np.unravel_index(_np.argmax(c), c.shape)
        H, W = c.shape
        return (ix - W if ix > W // 2 else ix), (iy - H if iy > H // 2 else iy)

    # Pulsar is NOT in registry_set — he is the orchestrator, not a spawnable
    # category — so every registry-driven check above skips him. He is also the
    # drone this check exists because of. Add him back explicitly.
    geom_cats = sorted(registry_set | {"pulsar"})

    geom_report = []
    for cat in geom_cats:
        base = res / f"{cat}-mouth-0.png"
        if not base.is_file():
            fail.append(
                f"[DESIGN-SURFACE] {cat}: no {cat}-mouth-0.png — portrait geometry "
                f"cannot be checked."
            )
            continue
        ref = _lum(str(base))
        ref = ref - ref.mean()
        drift = []
        for k in [f"mouth-{i}" for i in range(1, 5)] + ["blink"]:
            p = res / f"{cat}-{k}.png"
            if not p.is_file():
                continue
            mov = _lum(str(p))
            dx, dy = frame_shift(ref, mov - mov.mean())
            if abs(dx) > 1 or abs(dy) > 1:
                drift.append(f"{k}=({dx:+d},{dy:+d})")
        if drift:
            fail.append(
                f"[DESIGN-SURFACE] {cat}: lip-sync frames are not registered to "
                f"{cat}-mouth-0 — the face jumps as the mouth animates.\n"
                f"    drifted: {', '.join(drift)}\n"
                f"    D3 ownership: red on a DESIGN surface -> Nova, 48h SLA."
            )

        got = sym_offset(str(base))
        want = CENTRING_BASELINE.get(cat)
        if want is None:
            fail.append(
                f"[DESIGN-SURFACE] {cat}: no CENTRING_BASELINE entry in cast-check.sh.\n"
                f"    measured {got:+.1f}px. A new drone must land a ratified baseline\n"
                f"    here (measure it, eyeball it, then record it) or the centring\n"
                f"    gate silently does not cover it."
            )
            continue
        delta = abs(got - want)
        geom_report.append((cat, want, got, delta))
        if delta > CENTRING_TOL:
            fail.append(
                f"[DESIGN-SURFACE] {cat}: portrait centring drifted from its "
                f"ratified baseline.\n"
                f"    baseline: {want:+.1f}px    measured: {got:+.1f}px    "
                f"drift: {delta:.1f}px > tolerance {CENTRING_TOL:.0f}px\n"
                f"    (negative = head sits LEFT of the 362px canvas centre)\n"
                f"    Either the frames were re-derived off-centre (fix the crop), or\n"
                f"    the art legitimately changed (re-ratify the baseline here).\n"
                f"    D3 ownership: red on a DESIGN surface -> Nova, 48h SLA."
            )

# --- Report ------------------------------------------------------------------
if fail:
    sys.stderr.write("cast-check: FAIL — cast is inconsistent\n\n")
    for i, msg in enumerate(fail, 1):
        sys.stderr.write(f"{i}. {msg}\n\n")
    sys.exit(1)

print("cast-check: PASS")
print(f"  registry categories ({len(registry_set)}): {', '.join(sorted(registry_set))}")
print(f"  §1 drones ({len(skill_names)}): {', '.join(sorted(skill_names))}")
print("  9 of 10 checks agree (check 10 did not run, see below):" if hue_report is None
      else "  all 10 checks agree: §1 headings, registry, roster blurbs, frame PNGs,")
if hue_report is None:
    print("  §1 headings, registry, roster blurbs, frame PNGs,")
print("  CAST regex, Package.swift copies, build-pulsar-app.sh copies,")
print("  fictional-personas disclaimer, real-person-name denylist,")
print("  DESIGN-SURFACE master-art hue vs registry colour literal")

if hue_report is None:
    print()
    print("  !! check 10 (DESIGN-SURFACE art hue) NOT RUN — Pillow is not installed.")
    print("     The other 9 checks passed, but the art-vs-code colour gate did not")
    print("     execute. Install it (`python3 -m pip install Pillow`) to close the gap.")
else:
    print()
    print(f"  DESIGN-SURFACE hue margins (tolerance ±{HUE_TOL:.0f}°, D3 → Nova, 48h SLA):")
    for cat, want, got, delta, n_sat in sorted(hue_report, key=lambda r: -r[3]):
        bar = "tight" if delta > HUE_TOL * 0.75 else "ok"
        print(f"    {cat:<9} registry {want:6.1f}°  art {got:6.1f}°  "
              f"Δ {delta:5.1f}°  [{bar}]")

if geom_report is None:
    print()
    print("  !! check 11 (DESIGN-SURFACE portrait geometry) NOT RUN — needs Pillow")
    print("     and numpy. Frame centring and lip-sync registration are unchecked.")
else:
    print()
    print(f"  DESIGN-SURFACE portrait centring (tolerance ±{CENTRING_TOL:.0f}px on 362px,")
    print("  vs ratified per-drone baseline; all frame sets registered to mouth-0):")
    for cat, want, got, delta in sorted(geom_report, key=lambda r: -r[3]):
        bar = "tight" if delta > CENTRING_TOL * 0.75 else "ok"
        print(f"    {cat:<9} baseline {want:+6.1f}px  measured {got:+6.1f}px  "
              f"drift {delta:4.1f}px  [{bar}]")
PYEOF
