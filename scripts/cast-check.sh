#!/usr/bin/env bash
# cast-check.sh — field-aware cast-consistency gate for the Pulsar drone
# roster. Ratified R4 (Ship-now 3, 2026-07-30): the drone cast is a single
# fact spread across nine files (skill doc, Swift registry, roster UI, the
# frame-set PNGs, the spawn-categoriser regex, two build manifests, and the
# fictional-personas disclaimer) — nothing enforced them agreeing until now.
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

# --- Report ------------------------------------------------------------------
if fail:
    sys.stderr.write("cast-check: FAIL — cast is inconsistent\n\n")
    for i, msg in enumerate(fail, 1):
        sys.stderr.write(f"{i}. {msg}\n\n")
    sys.exit(1)

print("cast-check: PASS")
print(f"  registry categories ({len(registry_set)}): {', '.join(sorted(registry_set))}")
print(f"  §1 drones ({len(skill_names)}): {', '.join(sorted(skill_names))}")
print("  all 9 checks agree: §1 headings, registry, roster blurbs, frame PNGs,")
print("  CAST regex, Package.swift copies, build-pulsar-app.sh copies,")
print("  fictional-personas disclaimer, real-person-name denylist")
PYEOF
