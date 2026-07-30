# SPEC-R1 — Nova (Reviewer B, build-feasibility lens)

**Verdict: BUILDABLE, but steps 3–6 need Rev-2 surgery.** Step 3 is the exact path I
proved fails today. Step 5 omits the swarm asset (script stale, missing Meridian).
Step 6's hue gate has **2.2° of headroom on Nova** and can PASS while blind.

## 1. Step 3 rewrite — composite, never generate a sheet

Evidence: `atlas-mouth-1..4` differ from `mouth-0` only inside a 45×40px box
(0.46%→1.08% of pixels); `atlas-blink` only in the eye band (4.74%). The rest is
bit-identical. Drift isn't *corrected*, it's absent. Replace steps 3+4 with:

> **3. Build the frame set by compositing onto the approved master. Never ask the
> generator for a strip.** Codex cannot render a 6:1 sheet — it silently falls back
> to six independent 1:1 frames with per-cell **scale** drift. Phase correlation
> corrects translation but NOT scale, so the drift survives alignment and ships as
> the jagged-blink defect.
>
> a. Resize the approved master once → 362×362 LANCZOS. This is `base`. Every frame
>    is `base` + one local patch.
> b. Locate the mouth aperture and eye band on `base` (Atlas: x158–203, y193–233).
> c. **Erase the existing mouth glyph — accent-weighted lerp to plate:**
>    - plate `P` = median of the pixel ring just outside the mouth bbox (the drone's
>      own visor, so it inherits that visor's gradient and grain)
>    - accent unit `A` = normalise(`accent_rgb` − `P`)
>    - per pixel `w` = clamp(dot(px − P, A) / |accent_rgb − P|, 0, 1), smoothstepped
>    - `out = P + (px − P)·(1 − w)` — lerp toward plate, weighted by how much that
>      pixel carries the accent
>    Colour-agnostic: swap `accent_rgb` for the registry literal and it lifts green
>    off Nova or coral off Iris exactly as it lifted grape off Atlas. Feather the
>    weight mask (2–3px gaussian) — no hard patch seam.
> d. Paint the five mouth states into the cleared plate in the drone's own accent
>    with a warm interior falloff: closed → slight → half → more → wide-O. Same
>    centre, monotonically growing aperture.
> e. Blink = `base`, eye band cleared the same way, lidded eyes painted.
> f. **Assert:** numpy diff of every frame vs frame 0 is exactly zero outside its
>    declared bbox. This replaces phase correlation entirely.

Keep old step 4 only as a fallback check for legacy sheets, labelled as such.

## 2. Identity anchoring

The failure is a *symmetric* two-reference prompt. Fix is asymmetric roles:

- **"Image 1 is THE CHARACTER — preserve identity exactly. Image 2 is a MATERIAL AND
  LIGHTING REFERENCE ONLY — copy its finish, never its face."**
- Paste that drone's FACTORY-STYLE row in as a must-survive checklist (colour, gear,
  silhouette, expression, props).
- Explicit negative: *"Do NOT copy image 2's goggles, scarf, shoulder rig, chest
  emblem or face shape."*
- Name the **rules** from voyager, not voyager: brushed graphite, anodised trim,
  navy vignette, warm rim, seams. **Any gear not named comes back as Voyager's.**

## 3. Verification gates — ±35° hue is NOT sufficient

Measured now (`scripts/cast-check.sh`): **nova Δ32.8° against 35° — 2.2° of
headroom.** A Nova re-render trips it, or barely-passes while looking wrong.

- **(a) Tighten to ±20°, and fix Nova's existing art first.**
- **(b) Identity (auto):** perceptual-hash/histogram distance new-vs-old master;
  assert `0.15 ≤ d ≤ 0.55`. Below = nothing re-rendered; above = drifted.
- **(c) Distinctness (auto):** hue ≥40° from every *other* registry literal.
- **(d) Background (auto):** four corners navy (hue 210–240, V<0.25). Rule 6.
- **(e) Fill-the-square (auto):** non-bg pixels touch all four edges. Rule 8.
- **(f)** Eye catchlight and mouth interior depth stay eyeballed.

(b)–(e) are ~40 lines of numpy — write once, run over all 8.

## 4. Sequencing + cost

Per drone: 2–3 gen attempts × ~90s **sequential** + judgement ≈ 5–8 min. Compositing
≈5 min once the script exists; **first drone ≈45 min**, ~15 min after. **Total: 2.5–3.5
hours.**

- **Sequential:** codex gen calls (parallel chokes), per-drone visual judgement.
- **Batch:** all compositing, cropping, resizing and every gate above — one script
  over all 8, never per-drone hand-runs.
- **Sequence change:** render all masters → sign off the sheet of 8 → *then*
  composite. Compositing an unapproved master is the wasted work, and eight-up is
  the only way to judge "one cast" (the DoD).

## 5. Unbuildable as written

1. **Step 5 omits `assets/readme/drone-swarm.png`.** Any master change stales it, and
   `scripts/build-drone-swarm.py`'s CAST has **8 entries, no Meridian**, emitting a
   1868px single row — the shipped asset is **1256×1548** (a grid). Running it as-is
   *regresses* the README. Fix the script; add "rebuild swarm, verify 9 tiles".
2. **Step 6 is satisfiable while blind** — check 10 degrades to 9/10 and still exits
   0 without Pillow. Require the `DESIGN-SURFACE hue margins` block, not just exit 0.
3. **The pulsar row is unexecutable.** No `design/drones/pulsar.png` (check 10 skips
   him); his master is `assets/readme/pulsar.png`. State that or drop him.
4. **Meridian's scope undeclared** — in the table, but frames were rebuilt today.
5. **"Eight drones" vs the 9-row table.** Real set is 7 (+pulsar conditional).
