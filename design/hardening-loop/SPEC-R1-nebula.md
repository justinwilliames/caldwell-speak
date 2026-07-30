# SPEC-R1 — Nebula (creative direction) on FACTORY-STYLE.md

**Verdict: NOT READY. The eight rules describe Voyager's *ingredients*, not its *construction*.** A builder executing this ships eight recoloured Voyagers or eight barely-changed originals — and only finds out after all eight renders. Fix the four MISSING rules, unfix rules 1/3/5, add the banned-list and the pilot gate.

## MISSING rules (my eye vs. the reference)

**M1 — The face is a convex glass lens, not a screen.** *This is the single biggest gap.* Voyager's face is a physically curved smoked-glass faceplate with its own specular sheen; the eyes and mouth are lit apertures sitting *behind* it, and the glass reflection passes over them. Every one of the five siblings I viewed (sentinel, nova, echo, nebula, atlas) has a **flat black display panel with drawn vector glyphs** — that alone is why they read as a different factory. Add: *"The face plane is a convex tinted lens curving in three axes, carrying one soft specular highlight. Eyes and mouth are recessed lit apertures behind it. NEVER a flat rectangular display with drawn glyphs."*

**M2 — Non-metal materials are mandatory.** Voyager reads real because of the brown textile scarf and the webbing shoulder straps against the metal. No sibling has any non-metal. Add: *"Each drone carries ≥1 non-metal material — woven textile, leather strap, rubber gasket or ribbed bellows — occupying ≥8% of visible surface. Name it per drone."*

**M3 — No floating 2D graphics.** Echo's waveforms and Nebula's colour motes hover in the *background* as flat vector art. Voyager has zero. Add: *"Every element is a physical object in the scene with mass, shadow and DOF. Motifs must become hardware (emitter fins, a lit badge) or be deleted. NEVER glyphs floating in the background plane."*

**M4 — Accent distribution + saturation, quantified.** Voyager's brass is **desaturated (~55% sat), spread as ≥6 discrete hardware parts** (crown plate, brow band, temple wedges, chin bar, ear bezels, shoulder rings, chest emblem) at ~20% surface — and the *emissive* amber shares that exact hue, restricted to 5 sites. Siblings use 100%-saturation neon in continuous strips. Add: *"Accent metal 45–65% saturation, 15–25% of surface, ≥6 separate parts, never a continuous outline stripe. Emissive glow: ≤5 sites, same hue as the accent metal."*

**M5 — One light source, provably.** Both Voyager catchlights sit at 10 o'clock. Add: *"Key upper-left ~35°; warm rim (#FFD9A0, 30–50%) on upper-right helmet edge and both shoulder tops; catchlight at 10 o'clock in BOTH eyes; props >15% behind the face plane visibly soft."*

## WRONG / over-fitted rules

**R1 "weathered" contradicts the table.** Rule 1 mandates wear; the table says Echo "least wear", Sentinel "minimal". A builder will scuff Echo. Fix: separate **surface realism** (invariant: brushed directional grain, panel gaps as dark recesses with a lit upper bevel — a 200px crop of any flat area must never be one flat colour) from **wear (variance, 0–3)**: voyager 3, meridian 2, atlas 2, iris 1, nebula 1, sentinel 1, nova 1, echo 0.5.

**R1b "gunmetal/graphite" for all = nine grey robots** and kills Nebula's warm-lyrical and Iris's welcoming read. Fix: invariant is *value + finish* (mid-to-dark, non-glossy, brushed); permit up to 10% registry-hue tint in the chassis (warm-graphite Nebula, cool-graphite Sentinel).

**R5 "rounded dome" over-fits.** Sentinel's clipped precision lives in her faceted crown; a dome erases her silhouette. Fix: invariant = closed helmet + brow band + ear pods; **edge treatment is the variance axis**, hard-chamfered (sentinel, meridian) → fully rounded (echo, nebula).

**R3 "round eyes" over-fits** Atlas/Meridian gravitas — allow heavier-lidded, wider-than-tall apertures within "lit ring, real depth".

**R6 "roughly #0B1230→#1A2550"** yields nine different navies; Atlas and Nebula are already near-black. Make exact + checkable: *corner pixel #0B1230 ±6, centre-behind-head #1A2550 ±8.*

## Identity gaps (a re-render will destroy these)

- **sentinel:** missing — tick chest emblem, ball-tipped antenna, in-visor checkmark HUD, arched precise brows. **And she has NO mouth.** Spec must *adjudicate*: rule 4 grants her one; say so or the builder preserves mouthlessness.
- **nebula:** missing — the visible **hand** (only drone with one), headband arc, iridescent crown swoop, four-point sparkle emblem. **Her current eyes have eyelashes** — the no-cliché rule bans them but nothing says to REMOVE existing ones. Adjudicate explicitly, or "don't lose characteristics" wins.
- **nova:** missing — over-head headband arc, arched brows, shoulder-mounted soldering tip (not held).
- **echo:** missing — boom mic on a physical arm, perforated speaker crown, twin whip antennae, waveform chest badge.
- **atlas:** missing — headband arc, twin ball-tipped antennae, arched brows.
- **Canvas:** nebula.png and meridian.png are **1254×1254**, the rest 1024. Mandate exactly 1024×1024.
- **Gate trap:** cast-check asserts dominant hue ±35°. Darkening Nebula's pink-and-white chassis to graphite can flip dominance to the navy background and **fail the gate**. Warn, and require the accent to stay ≥15% surface.

## The single biggest execution risk + guard

**Risk:** the builder feeds codex-imagegen *two* image references (own master + voyager.png) and gets a blend — Voyager's goggles, brass brow and grin stamped onto every sibling. That is exactly the failure Justin pre-empted ("don't lose their characteristics"), and it only becomes visible side-by-side, after eight renders.

**Guard (three parts):**
1. **Never pass voyager.png as a face/gear reference.** Pass ONLY the drone's own master as an image reference; encode Voyager's style as a **verbatim HOUSE BLOCK of prompt text, identical for all nine**, plus a per-drone IDENTITY BLOCK written from that drone's own master. Add a verbatim **NEVER block** (no flat display face, no floating 2D glyphs, no glossy white plastic, no continuous neon strips, no eyelashes/lips, no pure black background) — negative constraints are what actually move image models.
2. **Pilot gate:** render **Sentinel first**, alone. She is the furthest from house style (glossy white, faceted, mouthless). View her at 128px beside voyager.png; do not render drone #2 until that pair passes. If the recipe can move Sentinel, it can move anyone.
3. **Contact-sheet gate, not solo review:** `montage design/drones/*.png -tile 3x3 -geometry 128x128+6+6 /tmp/cast.png` and judge THAT. Definition of done is a side-by-side claim — so it needs a side-by-side observation.
