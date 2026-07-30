# Pulsar drone factory style — Rev 7 (machined faces w/ pupils, articulated mouths)

**Reference master: `design/drones/voyager.png`.** Justin's ruling (2026-07-30):
*"Voyager is still the best one and should be the reference. They should look like
different robots out of the same factory."* · *"I like the features and colours they
have — just their style. Don't lose their characteristics / features and
accessories."* · *"Make sure they look like good matches to their voices too."*

A **material and render** standard, not a redesign. Every drone keeps its colour,
gear, silhouette and props. Only the *finish* changes.

> Rev 2 incorporates a four-lens hardening pass (Nebula art-direction, Nova
> buildability, Atlas user-outcome, Meridian counsel). Rev 1's verdict was NOT
> READY: it captured Voyager's ingredients, not its construction, and would have
> shipped eight recoloured Voyagers. Reviews: `design/hardening-loop/SPEC-R1-*.md`.

---

## A. INVARIANT — identical across the whole cast (this is "one factory")

1. **THE FACE IS FULLY MACHINED METAL — not a screen, and NOT a glass lens.**
   *(Justin's ruling, 2026-07-30, reversing Rev 1-4's highest-priority rule. The
   glass-dome direction produced faces he judged "too cartoony and silly... like
   they are TV screens for faces". Rev 4's §A1 was wrong and is retired.)*
   The face is built the way the body is built: machined plates, panel seams,
   chamfers, fasteners. Features are PHYSICAL MECHANISMS, not graphics:
   - **Eyes = mechanical camera-iris assemblies.** A turned metal bezel, visible
     aperture blades or a stepped iris ring, a real glass objective element set
     deep in the housing, lit from within. They should look like something that
     could physically focus. NOT a glowing outline, NOT a cartoon eye with a
     highlight dot, NOT an eye drawn on a panel.
   - **Mouth = a real machined aperture** — a speaker grille, a louvred vent, or
     articulated jaw plates. Machined depth, interior structure, actual edges you
     could catch a fingernail on. Backlighting is allowed; the *shape* must be
     mechanical.
   - **No black display panel of any kind**, no smoked dome, no faceplate the
     features are drawn onto. If you can describe the face as "a screen", it fails.
   **HIGH-IMPACT AND ROBOTIC is the target register.** Serious machinery, not a
   toy. Voyager remains the reference for MATERIALS and LIGHT; his face is the
   one part of him this rule supersedes.
2. **Chassis material: matte, brushed, light-absorbing metal** with visible panel
   seams and fasteners. Never glossy plastic, mirror chrome, or flat vector
   shading. (Value + finish are invariant; *hue* is not — see B4.)
3. **Accent colour is PHYSICAL METAL, not neon tape.** Anodised/enamelled trim
   panels, rings and bezels catching real light. Quantified: accent occupies
   **≥6 discrete physical parts**, at **45-70% saturation**; true emissive glow is
   limited to **≤5 sites** (eyes, mouth, chest sigil, and at most two others),
   sharing the metal's hue. No continuous 100%-saturation light strips.
4. **Eyes: MECHANICAL iris assemblies WITH A REAL PUPIL.** *(Justin's ruling,
   2026-07-30: "their eyes feel soulless without some form of pupil.")* A camera
   iris HAS a dark central aperture — so a pupil is more mechanically honest, not
   less. Build, outside in: turned metal bezel → anodised registry-colour ring →
   overlapping aperture blades → a lit annulus of registry-hex glass at full
   saturation → **a distinct DARK CENTRAL PUPIL: the actual aperture hole, reading
   deep and black, with the barrel interior visible in it.** The pupil is what gives
   the face a gaze; without it the eye reads as a lamp, not an eye. One real
   specular on the glass surface (upper-right); a specular on glass is not a cartoon
   catchlight dot. The lit annulus carries thumbnail identity (Atlas's ruling), the
   pupil carries the soul, and both are physical parts of the same mechanism.
5. **Mouth: an ARTICULATED MECHANISM THAT ACTUALLY OPENS — not a grille.**
   *(Justin's ruling, 2026-07-30: "the mouths need to be able to move mechanically
   from closed to open — so I'm not sure a grille is the right approach.")* A fixed
   grille of bars CANNOT open; the lip-sync frames need a mouth whose closed and
   wide-open states are visibly different hardware positions. Build it as one of:
   - **Articulated jaw plates** — an upper and lower machined plate meeting on a
     parting line, hinged on visible pivot pins, that separate to reveal a lit
     interior cavity. Closed = a tight seam with the pivots showing. Open = the
     plates swung apart, cavity and interior side walls exposed.
   - **A segmented iris shutter** — overlapping wedge plates that retract outward
     from the centre, the way a camera shutter opens.
   Either way: **frame 0 must read as CLOSED (a seam or a shut shutter, minimal
   light) and frame 4 as WIDE OPEN (plates clearly apart, cavity lit and deep).**
   The mechanism must be legible enough that a viewer understands how it moves.
   Interior is backlit so the open states read at 52px.
   *Adjudication:* Sentinel gains a mouth; every unit has the same feature set.
6. **At least one non-metal material** per drone — textile, leather, webbing,
   rubber. Voyager's scarf and straps are why he reads as built rather than
   rendered; no sibling currently has any.
7. **No floating 2D graphics.** Every element is a physical part in the scene.
   Echo's waveforms and Nebula's colour motes currently hover in the background
   plane — they must become emitters, etched plates, or physical particles.
8. **One light source.** Warm key from upper-left, cool rim from behind-right,
   shallow depth of field. Both eye catchlights sit at the **upper-RIGHT of the pupil (~1-2 o'clock)**, identical in both eyes — measured off the reference master, which is where the house look actually is. (Rev 2 said 10 o'clock; the pilot proved that is achievable but moves the drone AWAY from Voyager. Reference measured 2026-07-30.)
9. **Background: deep navy gradient vignette.** Corners ≈ `#02031A`, centre-behind-head ≈ `#1A2550`, tolerance ±14 per channel. Never hue-matched to the drone. (Re-baselined from the reference: voyager.png corners measure (2,3,23) and (1,2,25) — Rev 2's `#0B1230` was unreachable, four escalating attempts never got past (6,10,34).)
10. **Framing: the torso runs off the BOTTOM edge and the head is NEVER cropped**, with a thin margin (3-8%) above the crown; side gaps may be small but need not be zero. The complete crown and any antenna tip sit inside the frame with a thin margin above. (Rev 2 demanded all four edges; the reference itself touches only the bottom — top 0, left 0, right 0, bottom 124. Fill comes from the torso, never from slicing the skull.)

## B. MUST VARY — or the cast becomes nine identical robots

Rev 1's failure: applying every rule uniformly recreates the same-mold problem in
gunmetal. These axes are **required to differ**:

1. **Outer silhouette.** Shared *construction language*, never shared outline.
   Echo's dish, Iris's halo, Atlas's antennae, Nebula's crown swoop, Sentinel's
   faceted crown must survive and stay readable as a black-shape-only thumbnail.
2. **Edge treatment.** Soft-round ↔ faceted-angular is a variance axis, not a
   constant. Sentinel is faceted and precise; Nebula is curved and flowing.
3. **Wear level, 0–3** (0 = factory-fresh, 3 = heavily used). Uniform weathering
   flattens the age read the voice-match section depends on. Values in §C.
4. **Chassis tint.** Base value/finish is invariant, but up to **10%** of the
   registry hue may tint the metal — Nebula reading warm and Sentinel cool is
   correct, nine identical greys is not.

## C. Per-drone: identity to PRESERVE + voice character

**On the voice question — the team's ruling, adopted.** Meridian recommended
dropping the gender label and keeping the character cues; Atlas showed the
adjectives weren't checkable. Combined: the column below is **voice character**,
expressed as four ordinal axes a builder can hit repeatably. Justin's ask is
served — a viewer reads the voice off the build — without the spec ever asserting
a machine has a gender.

**Axes:** `jaw` = jaw/chassis width (1 narrow → 5 broad) · `eye` = eye-size ratio
to face (1 small → 5 large) · `wear` = 0–3 · `edge` = 1 faceted → 5 soft-round.

**EXPRESSION — the fifth axis (Justin's ruling, 2026-07-30):** *"make sure their
personas match their faces (e.g. some will look more friendly than others, more
serious, some more playful)."* A machined face still has expression; it just comes
from GEOMETRY rather than drawing. The three mechanisms, all physical:
- **Brow-plate rake** — raked down over the eyes = severe/hooded; level = neutral;
  lifted with more forehead showing = open, alert, friendly.
- **Mouth-aperture cant** — ends canted UP = warm (this is how a machine smiles);
  dead level with squared corners = neutral/clipped; ends canted DOWN or the
  aperture pinched narrow = grim.
- **Iris aperture openness** — blades wide open with a large lit element = alert,
  eager, welcoming; stopped down to a narrow polygon = scrutinising, guarded.

This is what recovers what the machined direction costs: the pilot's honest finding
was that Voyager *"looked pleased to see you"* before and reads stern after. He
should read WARM in machined terms — that is a spec requirement now, not a nicety.

| Drone | Expression target | Brow / Cant / Iris |
|---|---|---|
| voyager | warm, gruff, glad to see you | lifted / up / wide |
| sentinel | severe, scrutinising, exact | level-hard / level squared / stopped down |
| nova | eager, bright, playful | lifted high / up / widest |
| nebula | warm, dreamy, lyrical | soft-lifted / gently up / wide |
| echo | playful, keen, youngest | lifted high / up / widest |
| iris | welcoming, poised, confident | level-warm / slight up / open |
| atlas | calm, steady, unflappable | level / level / mid |
| meridian | grave, measured, senior | heavy and hooded / level and tight / stopped down |
| pulsar | warm authority — the host | open / slight up / wide |

| Drone | Colour | Voice | jaw / eye / wear / edge | PRESERVE these features |
|---|---|---|---|---|
| voyager | amber `#F2A83B` | Fred — gruff, retro, older | 4 / 3 / 3 / 3 | **REFERENCE — do not regenerate** |
| sentinel | azure `#6BB8EB` | Karen — crisp, clipped, precise | 2 / 3 / 1 / 1 | scanner lens over one eye, tick emblem, antenna, in-visor HUD, faceted crown; **gains a mouth** |
| nova | green `#5CD16B` | Samantha — bright, quick, eager | 2 / 4 / 0 / 4 | fusion-core chest, shoulder torch, headband arc |
| nebula | magenta `#E95CD1` | Moira — warm, lyrical, flowing | 2 / 4 / 1 / 5 | prismatic visor, brush, visible hand (only drone with one), crown swoop; **eyelashes removed** (§D) |
| echo | teal `#2EBFB8` | Junior — light, boyish, newest | 2 / 5 / 0 / 5 | comms dish, boom mic, perforated crown, waveform motif (physical) |
| iris | coral `#F26178` | Tessa — clear, warm, poised | 3 / 4 / 1 / 4 | halo ring, orbiting channel motes (physical) |
| atlas | grape `#8040C0` | Rishi — deep, steady, grounded | 4 / 3 / 2 / 3 | twin antennae, UX flow-path chest glyph (3 dots + routed elbow) |
| meridian | navy `#24427A` | Ralph — deep, slow, senior | 4 / 2 / 2 / 2 | barrister neck bands, gold scales emblem, pinstripes |
| pulsar | indigo `#818CF8` | Daniel — authoritative host | 3 / 4 / 1 / 4 | **LAST, conditional.** Master lives at `assets/readme/pulsar.png`, not `design/drones/` |

## D. NEVER (hard bans)

- No simulated human anatomy or gendered costume: **no eyelashes, lips, blush,
  bows, skirts, cinched or hourglass waists, breast-shaped chest plating, hip
  flare, or hair-like cable/antenna styling.** Character differs in proportion and
  bearing only — jaw width, shoulder-to-head ratio, chassis taper, scale, brow
  shape — never in simulated anatomy. (Meridian's wording, verbatim.)
- **Never pass `voyager.png` as an image reference to the generator.** It produces
  a blend — Voyager's goggles, scarf and grin stamped on everyone, the exact
  failure Justin pre-empted. The house style travels as the **text of §A** plus an
  explicit negative naming Voyager's goggles / scarf / shoulder rig / chest emblem.
  Any gear not named in §C comes back as Voyager's.
- No recognisable likeness of an existing copyrighted robot or character.

## E. Build method (the parts that actually work)

**E1. Master render.** codex-imagegen with **one** image reference: the drone's own
current master, framed as *"Image 1 is THE CHARACTER — preserve identity exactly."*
Paste §A verbatim as the HOUSE BLOCK, the drone's §C row as a must-survive
checklist, and §D as the NEVER block. Gens run **sequentially** — parallel codex
calls choke. Fresh filenames per attempt; codex won't overwrite.

**E2. PILOT GATE — render Sentinel first, alone, and stop.** He is furthest from
house style (flat panel, no mouth, faceted crown). If the prompt can't produce
Sentinel, it can't produce anyone; fix the prompt before committing seven more
renders. Do not proceed past Sentinel without a pass.

**E3. Masters first, sheets later.** Render all masters → judge them **eight-up on a
3×3 contact sheet at 128px** (the "one cast" claim is a side-by-side claim, so it
must be judged side by side) → only then composite frames. Compositing an
unapproved master is the wasted work.

**E4. Frames: GENERATE a sheet, crop, then ECC-align. Do NOT composite.**
*(Justin's ruling, 2026-07-30, reversing Rev 4's method.)* Measured proof: the
ORIGINAL shipped frames changed **6.19% / 26.45% / 12.38%** of the image
(mouth-2 / mouth-4 / blink vs mouth-0) across a bbox spanning the WHOLE face —
because each frame is a genuine re-render in which the jaw moves and the light
reacts. Rev 4's composite frames changed **1.4-3.2%** inside a small box, which
Justin correctly identified as "the mouths don't actually move, there is just a
coloured overlay moving" — an 8x regression in real movement. Drift-free and dead
is worse than slightly-drifty and alive.

The method that works, from the original playbook:
1. Generate a **6-cell sprite sheet** per drone via codex-imagegen from the
   approved master: one wide strip, 6 equal SQUARE cells, mouth closed → slight →
   half → more → WIDE OPEN → blink(eyes closed, mouth closed). Every cell a full
   re-render of the face; head position/size/framing/lighting held constant.
2. Crop at `width/6`.
3. **ECC-align with cv2** (`cv2.findTransformECC`, MOTION_EUCLIDEAN or
   MOTION_AFFINE, warping each frame onto frame 0). This is the step that makes
   generated frames usable — it corrects the translation AND scale drift that
   phase correlation cannot. cv2 4.13 is available on this machine. Aligned frames
   are the source of truth; **never re-crop from the sheet afterwards**.
4. If codex refuses a 6:1 strip and returns independent 1:1 renders, that is
   acceptable *provided* ECC alignment brings them into register — verify by
   measuring residual offset and the changed-pixel bbox. Reject any set whose
   frames differ by less than ~4% (that means the mouth isn't really moving) or
   whose head visibly shifts after alignment.
5. Sanity gate per drone: mouth-4 vs mouth-0 changed pixels **≥ 8%**, blink vs
   mouth-0 **≥ 5%**, and no visible head jump when the frames are flipped through.
6. **The mouth must MOVE, not just brighten.** Because §A5 is now an articulated
   mechanism, frame 0 is CLOSED (plates together, seam visible, little or no
   interior light) and frame 4 is WIDE OPEN (plates apart, cavity deep and lit).
   Reject any set where the aperture outline is constant and only the fill changes —
   that is the Rev 4 "coloured overlay" failure wearing a machined costume.
   Likewise the BLINK frame must show the aperture BLADES closing over the pupil,
   not the whole eye switching off.

**E5. Accent-glyph removal, generalised to any colour.** Plate `P` = median of the
pixel ring just outside the target bbox (inherits that drone's own visor gradient).
Accent unit `A` = normalise(accent_rgb − P). Per-pixel `w` =
smoothstep(clamp(dot(px−P, A) / |accent_rgb − P|, 0, 1)). `out = P + (px−P)·(1−w)`.
Swap `accent_rgb` for the registry literal per drone.

**E6. Placement.** 362×362 LANCZOS → `Sources/Resources/<drone>-mouth-0..4.png` +
`-blink.png`; master → `design/drones/<drone>.png`. **Also regenerate
`assets/readme/drone-swarm.png`** — and note `scripts/build-drone-swarm.py` is
currently BROKEN for this purpose (8-entry CAST with no Meridian, single-row layout
emitting 1868px wide, while the shipped asset is 1256×1548 grid). Fix the script
first or the README regresses to an eight-drone lineup.

## F. Gates — automated before eyeballed

Run over all eight in one pass (~40 lines of numpy):

1. **Hue vs registry literal: ±20°** (tightened from ±35°). Nova's current master
   sits at Δ32.8° — it must be brought inside tolerance by its own re-render, not
   by loosening the gate.
2. **Cross-drone distinctness: ≥15°** from every other registry literal. (Rev 2 said 40°, which is mathematically impossible for this palette before a single render: sentinel↔meridian 15.2°, meridian↔pulsar 15.4°, sentinel↔echo 26.8°, sentinel↔pulsar 30.5°, atlas↔pulsar 35.5°. In the blue cluster, separation is carried by SILHOUETTE, not hue — which is why §B1 is mandatory.)
3. **Identity distance — RETIRED as an absolute band.** The 0.15-0.55 band was estimator-undefined and unusable: measured with mean per-pixel RGB L2 at 128px, the approved pilot scores 0.178 and two ENTIRELY DIFFERENT drones score only 0.238, so nothing can reach 0.55. Replaced by a relative reading: the re-render should land at **60-100% of the approved pilot's transformation magnitude** on whatever estimator the builder states. State the estimator; quote the number.
4. **Background: corner pixels navy** within §A9 tolerance.
5. **Framing: subject touches the BOTTOM edge; thin margin above the crown; head uncropped** (see §A10 as amended).
6. **Thumbnail acceptance:** downsample to 52px — the drone must be identifiable
   from silhouette + eye colour alone, in under a second. This is the product's
   actual job; a master that fails it fails, however beautiful at full size.
7. `bash scripts/cast-check.sh` must PASS **and print its `DESIGN-SURFACE hue
   margins` block** — the check degrades to "9 of 10" and still exits 0 when Pillow
   is absent, so exit code alone is not proof it ran.

Detail budget follows the thumbnail (Atlas's finding): micro-wear, rivets and vents
are invisible at 52px. Spend the render on **eye-colour saturation, outer-silhouette
accessories, and framing** — not surface noise.

## G. Provenance (Meridian, required)

Record per drone at generation time in `design/drones/PROVENANCE.md`: model +
version, full prompt text, reference images used by filename, date, and the
attestation *"no real-person likeness; not modelled on a third-party copyrighted
character."* References being the project's own prior masters removes third-party
rights-chain risk for the style reference, but the record is still required — the
answerable question is resemblance to existing IP, not reference provenance.
Also add a one-line AI-generation disclosure near the portraits in the README, and
state once whether MIT covers the art assets or only the code.

## H. Definition of done

Seven re-rendered drones (Pulsar conditional, Voyager untouched) viewed **eight-up
at 128px and again at 52px**: one cast, same materials, same lighting, same
background, same construction — distinguishable instantly by colour, silhouette and
gear. All §F gates green. Provenance recorded.

---

## I. Build lessons — binding on every remaining render (from the first three)

1. **The canonical template is `prompt-a4.txt`, not `prompt-a2.txt`.** a4 is the
   hardened pilot prompt (explicit mouth pixel sizing, per-unit mouth shape, harder
   framing). Anyone templating from a2 ships a weaker mouth. *(Echo caught this
   after the orchestrator pointed two builders at the wrong file.)*
2. **MAX THREE DELTAS PER RETRY.** The generator has a fixed attention budget:
   bundling six re-render instructions made it DROP house-block items it had already
   nailed — the mouth and the anti-float rule go first. Echo's a2 regressed both
   things a1 got right. Fix ≤3 things, re-render, repeat.
3. **The template's §A8/§A9 text is STALE (Rev 2) — flip §A8 when you use it.**
   It demands the 10 o'clock catchlight and forbids upper-right, the exact inverse of
   §A8 as amended. Flip it. §A9's stale near-black wording is deliberately KEPT: it
   empirically lands corners inside the Rev 3+ band (4/4 on two drones), whereas
   asking for the literal target risks crushing below the blue floor.
4. **Eye brilliance fights hue discipline.** Asking for bigger/brighter eyes pulled
   Nova's whole green family yellow-ward and blew the hue gate. The safe delta is
   geometric only: *"the ring is a larger circle of the SAME colour — do not brighten
   or shift it."*
5. **Mask the backdrop before measuring hue.** A naive dominant-hue estimator counts
   a brightened background into the saturated-pixel set and reports nonsense (151°
   for a render that was actually 93°). Reusable tools left in the scratchpad:
   `hue2.py` (backdrop-masked) and `measure.py`. Report the MODAL hue — that is what
   §F1 names.
6. **Vary the non-metal parts per drone.** Naming specific parts is mandatory (a
   generic "add a non-metal material" produced nothing at all); reusing another
   drone's parts is a factory-clone failure. Used so far: Sentinel = rubber
   concertina neck boot + woven ballistic collar; Nova = quilted shoulder pad +
   ribbed rubber torch hose; Echo = open-cell foam windscreen + braided cable sleeve.

## J. Machined-face pilot learnings (binding — from Voyager + Sentinel)

1. **Two-stage chain beats one shot.** Base face-rebuild prompt → then a NARROW
   correction pass whose input is the stage-1 output, opening with a *"what the last
   render got right — preserve all of it"* block. That block is what stops the
   generator trading away wins while fixing a miss.
2. **Point at a part the input already gets right.** The single highest-leverage
   line in the winning Voyager prompt was: *"Look at the FOREHEAD LAMP in Image 1 —
   a turned brass bezel, a stepped ring, a deep-set warm amber element. That part is
   the reference for how the new eyes and mouth must be built."* Every drone has an
   equivalent already-machined part. Find it and point at it.
3. **Name the failure in the generator's own terms:** *"two flat glowing rings with
   black cartoon pupils and a highlight dot, and a grin shaped like a decal — those
   are GRAPHICS, not machinery."* Naming beats describing the target alone.
4. **Fold these three corrections into the BASE prompt** (they were needed as a
   second pass on both pilots): the lit glass objective must fill ~55-60% of turret
   diameter or the eyes read as dark rings with a speck at 52px; the mouth cavity
   must be explicitly BACKLIT or it reads as a dead grey box; a secondary optic must
   stand visibly PROUD on a bracket or it collapses into the eye.
5. **Add to the house block:** *"no glowing bars or lights anywhere on the face
   other than the two eye elements and the mouth interior."* Voyager's m4 grew two
   stray amber bars under the eyes when a correction block dropped that line.
6. **Mechanising the eyes IMPROVED thumbnail identity, both pilots.** Sentinel's
   accent-carrying pixels went 12.9% → 18.0% at 52px; Voyager's amber outlines used
   to dither into rings and now punch through as solid lamps. The §A4 worry was
   unfounded — a lit glass element beats a drawn ring at small size.
7. **Run gens BACKGROUNDED.** The foreground shell timed out at 10 minutes while
   codex kept working and still wrote the file.
