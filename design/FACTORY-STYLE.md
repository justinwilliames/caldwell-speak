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
| meridian | navy `#24427A` | Ralph — deep, slow, senior | 4 / 2 / 2 / 2 | **ARMOURED, not suited (Justin, 2026-07-30)** — see note below |
| pulsar | indigo `#818CF8` | Daniel — authoritative host | 3 / 4 / 1 / 4 | **LAST, conditional.** Master lives at `assets/readme/pulsar.png`, not `design/drones/` |

**Meridian's body — REDESIGN (Justin's ruling, 2026-07-30):** *"I don't like that
Meridian is in a lawyer suit, can we make it more subtle but still more in armour
like the rest? I still want him to look cool."* He is the only unit wearing
clothing rather than armour, which breaks the one-factory read — a robot in a
pinstripe suit is a costume, and it reads as a gag rather than as the cast's most
senior member.

- **OUT:** the pinstripe wool suit, the lapels, the visible barrister neck bands as
  cloth tabs. No tailoring, no suiting fabric, no shirt-and-tie logic.
- **IN:** heavy machined armour in the house language, same construction as his
  siblings — layered navy anodised plates, chamfers, fasteners — but the **heaviest
  and most formal** set in the cast: thicker plates, a higher standing gorget
  collar, more overlap, a deliberate ceremonial weight. Think honour-guard
  plating, not office wear.
- **Authority survives as INSIGNIA, not tailoring.** The gold scales emblem stays
  as a cast-brass badge. His barrister bands become **two slim vertical white
  ceramic or enamelled inlay strips** set into the gorget where the cloth tabs
  were — same visual signature at 52px (they are his strongest thumbnail mark),
  now a machined part. Optionally one restrained gold pinstripe as an engraved
  line in the plate, not a woven cloth pattern.
- Keep him the oldest-reading and gravest unit; formal now comes from the weight
  and symmetry of the armour, not from a suit.
- **FRAMING NORMALISES TOO (Justin, 2026-07-30):** *"that should mean you can zoom
  Meridian in more so his head is more central like the rest."* His head has sat
  high in the frame since his first render — accepted at the time as the price of
  fitting the suit, the neck bands and the chest scales into shot. With authority
  moving to insignia, that constraint is gone: **zoom in so his head is centred and
  the same relative size as his siblings**, torso running off the bottom edge, thin
  margin above the crown (§A10). He should sit in frame like the rest of the cast,
  not pulled back to accommodate a costume.

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

---

# REV 8 — FULL CHARACTER REDESIGN (Justin's brief, 2026-07-30 ~21:30, overnight run)

**This supersedes the "face-only" scope of Rev 5-7.** Justin's brief verbatim:

> "Make sure by the morning I have all 9 designed, fully mechanical movement in the
> mouth (as in it should properly open/close — think iron man or transformers how it
> all properly moves) and I want them to still all be approachable / friendly and
> aligned to their personalities. Also Pulsar needs a redesign too. Also all 9 of
> them should be visually distinct with different accessories, accent colour, helmet
> shapes/styles, and accessories/textures in or on their armor (i.e. i like voyagers
> little red scarf and novas leatheresque shoulder pads). Also make sure that the new
> characters still blink when passive it makes them feel alive. Also make sure that
> they all have glowing orbs in the centre of their chest and that they each have
> glowing accents/items so they feel powered up somewhat. Nova is a good example of
> this. Also make sure that their armor and accessories clearly matches their role.
> You also do have the freedom to completely redesign their aesthetic if you think
> that it is warranted. And when I say Aesthetic i mean their helmet shapes,
> character, accessories, colour, etc - keep the art style we agreed on that you have
> been building now."

## R8.1 — Scope: ALL NINE get a full redesign
voyager · sentinel · nova · nebula · echo · iris · atlas · meridian · **pulsar**.
Rev 5-7's approved face-only masters are NO LONGER FINAL — they are inputs at best.
**Voyager is no longer sacred as an untouched master**; he is redesigned too. What
survives from him is the *art style* (materials, lighting, render quality) and his
own identity cues (amber, scarf, lamp, prospector read).

## R8.2 — KEEP THE AGREED ART STYLE (non-negotiable)
The house look built across Rev 5-7 stays: matte brushed metal with real panel seams
and fasteners, physical anodised accent metal (not neon tape), a **fully machined
face** (no screens, no glass domes, nothing drawn on), mechanical iris eyes **with a
dark central pupil**, one real specular on real glass, deep navy gradient vignette
background (corners ≈#02031A ±14), warm key upper-left + cool rim behind-right,
shallow depth of field, tight hero crop with the head uncropped and a 3-8% margin
above the crown, torso off the bottom edge. Premium 3D, Pixar/Apple-keynote grade.
**Freedom applies to the CHARACTER (helmet, silhouette, accessories, gear, textures,
accent hue), NOT to the rendering language.**

## R8.3 — MOUTH: properly mechanical, Iron Man / Transformers grade
The mouth is a **multi-part machined mechanism that visibly TRANSFORMS between
closed and open** — interlocking plates that slide, hinge and separate, with visible
pivots, tracks, linkages and interior structure revealed as it opens. Not a grille.
Not a lit slot. Not an outline whose fill brightens.
- **Frame 0 = fully CLOSED:** plates seated together, a tight parting seam, minimal
  interior light. It should look sealed.
- **Frame 4 = fully OPEN:** plates clearly swung/slid apart, the interior cavity deep
  and lit, mechanism (pivots/linkage) visible in the gap.
- Frames 1-3 are genuine intermediate positions of the same hardware.
The test: flip 0→4 and it must read as a machine **operating**, the way an Iron Man
faceplate or a Transformers panel sequence reads.

## R8.4 — BLINK IS MANDATORY (passive liveness)
Every unit keeps a blink frame, and blink = **the mechanical iris aperture blades
closing over the pupil** (or a machined lid plate sweeping down), not the eye
switching off. The app fires blinks during pauses; this is what makes them feel
alive when idle. A cast that doesn't blink is a cast of statues.

## R8.5 — POWERED-UP: chest orb + glowing accents, every unit
- **Every drone has a GLOWING ORB at the CENTRE OF ITS CHEST** — a recessed spherical
  or lensed core emitting in that drone's accent hue, with visible housing, ring and
  interior depth. Nova's fusion core is the reference.
- **Every drone has additional glowing accents/items** so it reads as powered up:
  emitter beads, lit seams in recesses, an illuminated tool or instrument, lit vents.
  Enough to feel energised — but the accent metal still dominates over emission, and
  §D's "no glowing bars on the face other than eyes and mouth interior" holds.

## R8.6 — APPROACHABLE AND FRIENDLY, per personality
The machined direction must NOT read cold or hostile. All nine stay **approachable**;
they differ in *how* warm. Expression is still geometry (brow rake, mouth cant, iris
openness — §C's EXPRESSION table stands), but the floor is friendly: even Meridian
and Sentinel read as composed and trustworthy rather than menacing. If a render
looks like a threat, it fails.

## R8.7 — VISUAL DISTINCTNESS: five axes, no two units alike
Each drone must differ from all others on ALL of these:
1. **Helmet shape/style** — silhouette must be unique and readable as a black shape
   at 52px (crest, dome, faceted crown, dish, halo, swoop, yoke, gorget, hood…).
2. **Accent hue** — the registry literal, ≥15° apart (§F2).
3. **Accessories/gear** — role-specific, listed per drone in §C.
4. **Texture/material accents on the armour** — the thing Justin singled out:
   *"i like voyagers little red scarf and novas leatheresque shoulder pads."* Every
   unit needs at least one distinctive non-metal material with real character, and
   no two units may share one. (Running list in §J.6 — extend it, never reuse.)
5. **Armour silhouette weight** — heavy/ceremonial through light/agile.

## R8.8 — ARMOUR AND GEAR MUST MATCH THE ROLE (read at a glance)
A stranger should be able to guess the job from the kit:
| Drone | Role | Armour + gear direction |
|---|---|---|
| voyager | explorer / data scout | expedition rig: forehead lamp, amber goggles pushed up, the red scarf, webbing, sample pouches, worn plating |
| sentinel | reviewer / security | inspector's plate: scanner optic, precise clean armour, minimal wear, a tick/verified insignia, hard chamfers |
| nova | builder | workshop rig: leather-ish shoulder pads, torch/welder, tool hose, fusion core, scuff-free factory-fresh plate |
| nebula | creative director | atelier rig: prismatic visor element, brush, linen apron, cork grip, paint-flecked plate, the visible hand |
| echo | growth / comms | comms rig: dish, boom mic, foam windscreen, braided cable, waveform plates, lightest armour, youngest read |
| iris | marketing | signal rig: halo ring, orbiting channel charms, felt gasket, elegant poised plate |
| atlas | UX / all-rounder | field-generalist rig: twin antennae, flow-path badge, leather tool roll, waxed canvas, broad steady plate |
| meridian | counsel | **honour-guard plate (NOT a suit)** — heaviest, most formal, high gorget collar, white ceramic inlay strips, cast-brass scales badge, one engraved gold line |
| pulsar | host / orchestrator | **conductor's rig — REDESIGN REQUIRED.** He must read as the one in charge and the friendliest: a distinctive crest or crown that says host, indigo, suede ear cushions, knitted collar, the four-point star as a lit chest orb. Most approachable face in the cast. |

## R8.9 — Order of work (overnight)
Pilot **Meridian** first (biggest change: armour + framing + face + mechanism). Then
**Pulsar** (most-seen, full redesign). Then voyager, sentinel, nova, nebula, echo,
iris, atlas. One unit per turn, sequential gens, backgrounded, ≤4 attempts each,
MAX THREE DELTAS PER RETRY. Then frames (§E4 sheet + cv2 ECC, gates in §E4.5/4.6),
then assets, then verify. `git push` is GATED — halt and notify.

## R8.10 — Two corrections from the frames pilot (Justin, 2026-07-30 ~23:15)

**(a) THE MASTER MUST SHOW THE MOUTH FULLY CLOSED.** *"in this static one his mouth
is already half open too — so make sure it can be fully closed as well."* Meridian's
approved master renders the jaw slightly parted, which means frame 0 has nowhere to
close TO — the resting state should be sealed. **Every master renders with the mouth
SEALED SHUT:** plates seated metal-on-metal, a tight parting seam, teeth interlocked
in their sockets, minimal interior light. The mechanism must still be legible (pins,
knuckles, tracks visible) so a viewer sees how it *would* open — but the default state
is closed. Frame 0 then matches the master, and frames 1-4 open from a true zero.
Meridian's master needs one corrective pass for this.

**(b) FACIAL GEOMETRY VARIES WITH CHARACTER — keep who they already are.**
*"remember some of the other agents are more friendly-looking etc — and will have
rounder more friendly mouths, eyes and facial shapes. I still want to retain the
general feeling of each of them. They should still feel like their original
characters just enhanced."* Meridian is the cast's severe extreme — square teeth,
hard chamfers, a heavy lintel brow, narrow stopped-down irises. **Do NOT carry his
geometry to the friendly units.** The MECHANISM is shared (iris assembly with a
pupil; multi-part jaw on pivots with a lit cavity); its SHAPE LANGUAGE follows the
character:
| Character read | Eyes | Mouth aperture | Face plates |
|---|---|---|---|
| voyager (warm, gruff) | large round irises | wide, softly curved, generous | rounded plates, soft chamfers |
| sentinel (precise) | medium, crisp circular | narrow, level, squared | faceted, hard chamfers |
| nova (eager) | LARGE round, wide-racked | broad, curved UP, big travel | soft-radiused, friendly |
| nebula (lyrical) | large, soft round | gently curved up, flowing | most filleted in the cast |
| echo (playful, youngest) | LARGEST round irises | rounded, up-canted, wide | softest, rounded, chunky |
| iris (welcoming) | large round, open | softly curved, slight up-cant | elegant curves |
| atlas (calm) | medium round | level but softly cornered | broad, mid chamfers |
| meridian (grave) | small, stopped down | level, tight, squared teeth | heavy, hard, hooded |
| pulsar (warm host) | large round, open | curved, welcoming, up-cant | rounded, approachable |
**The test: each redesign must still be recognisable as THAT character to someone who
knew the old cast — enhanced, not replaced.** Compare each render against the unit's
pre-Rev-8 master and confirm the family resemblance survived; if it reads as a new
robot wearing the old colour, it fails.

## R8.11 — Frames pipeline, PROVEN (carry to all nine)
The pilot passed with no mechanism change needed. Reusable specifics:
- **3×2 grid at 1536×1024** (six exact 512×512 cells) — codex will not take a 6:1
  strip. Cells land on exact pixel boundaries; crop at width/3, height/2.
- **Mask the mouth band OUT of the ECC alignment input**, or the mechanism change
  drives the alignment. MOTION_EUCLIDEAN sufficed on all frames; AFFINE never fired.
  Residuals ≤0.92px, scale 1.0000.
- **Pin registration with explicit pixel targets per cell** (crown N px below cell
  top, eye centre line, mouth parting line, helmet span) — this is what produced
  sub-pixel residuals across independent re-renders.
- **Name the PARTS that must become visible** as it opens (teeth clearing sockets,
  pins at the end of their tracks, linkage arms in the gap) plus a numeric gap target.
  Naming parts is what stopped the generator brightening a fill instead.
- **Gate recalibration (pilot finding):** the spec's 6.19/26.45/12.38% figures were
  measured on 1024px sources, not the shipped 362px frames — on the shipped surface
  the real Voyager reference is 1.04/4.85/3.33%, so the absolute ≥8%/≥5% thresholds
  are mis-scaled and Voyager himself would fail them. **Use the geometric test as
  primary: the aperture GAP must grow monotonically (Meridian: 13→60px, 4.6×) and the
  change bbox must span the whole frame** (a change confined to a small box is the
  coloured-overlay fake — the shipped Rev 4 Meridian frames changed 97% of pixels
  inside an 89×13px box and nothing outside it). Blink: judge per-eye-box (≥12%),
  not full-frame.

## R8.12 — Maximum jaw travel: dial it back (Justin, 2026-07-31)

*"his mouth looks like it has extended a little bit too far - do slightly less."*
The pilot's frame 4 opened to a **60px gap at 362px** (4.6× the closed seam). That
is past the point where it reads as speech and starts to read as a hinge failure.

**New target for frame 4 (widest): ~40-45px gap at 362px** — roughly 3-3.5× the
closed seam, not 4.6×. The intermediate frames scale with it:
| frame | gap @362 (target) | reads as |
|---|---|---|
| 0 | sealed, 0-8px seam | closed, plates seated |
| 1 | ~14px | barely parted |
| 2 | ~24px | mid |
| 3 | ~34px | open |
| 4 | **~40-45px** | widest — a wide vowel, NOT a dropped jaw |
Keep the mechanism identical (teeth clearing sockets, pins in tracks, linkage
visible, lit cavity) — only the maximum travel reduces. The linkage should still be
visible at frame 3-4; if pulling the travel back hides it, favour showing the
mechanism over hitting the exact number.

## R8.13 — Eye/mouth clearance (Justin, 2026-07-31: "voyager's eyes blur into his mouth")

Voyager's r4 seats the eye turret's lower bezel almost directly on the mouth's
up-canted arc. With no machined surface between them the two assemblies merge into
one shape — the eye "blurs into" the mouth, and the face loses its structure.

**RULE:** there must be a **clearly readable machined CHEEK PLATE between the bottom
of the eye bezel and the top of the mouth bezel** — its own surface, with a panel
gap or chamfer line on at least one side, at minimum **~8% of frame height
(≈80px at 1024, ≈28px at 362)** of clear metal. The eye assembly and the mouth
assembly must read as two separate pieces of hardware bolted into a face, never as
one continuous form.

Highest risk on the units with WIDE UP-CANTED mouths whose arc ends rise toward the
eyes — voyager, nova, echo, iris, pulsar, nebula. When the mouth cants up, the ends
must NOT rise into the eye zone: cant the *centre* line, keep the arc's extremities
below the clearance band. Check this at 52px too — if the eye and mouth merge into a
single blob at thumbnail size, it fails.

---

# REV 9 — EMOTIVE TARGETS, SUBTLE MOUTHS, PER-UNIT VOICE (Justin, 2026-07-31)

Rev 8 delivered the machinery. Rev 9 fixes what the machinery did to the
CHARACTERS. Justin's verdict on the Rev 8 cast: *"The fact that their mouths are
like zig-zaggy/interlocked makes them look creepy and less friendly. The only one
I am sold on is Meridian."*

## R9.1 — THE TEETH ARE THE PROBLEM. Kill them.

The interlocking-teeth jaw reads as a **grimace** on every face except the one
character who is supposed to be severe. It was carried cast-wide because it made
the mechanism legible; it made eight units creepy.

**NEW MOUTH STANDARD — a small, subtle, moving SLIT.** Justin's reference is the
ORIGINAL Pulsar: *"mouths can be smaller and more subtle like a small slit that
moves like the original pulsar had. The mechanical movement is good but make it
much more subtle and smaller."*

- **NO teeth. NO zig-zag. NO castellations. NO interlocking lugs.** Not on any
  unit. The parting line is a clean machined SEAM, straight or gently curved.
- **Much SMALLER.** The aperture is a slim horizontal slot, roughly **45-60% of
  the width** the Rev 8 mouths occupied, and shallow.
- **The mechanism stays, but quietly.** Two machined plates meeting on a clean
  seam, with pivot pins and a fine clearance gap visible at the ends. It should
  read as *a machine that can open its mouth*, not as *a machine showing its
  teeth*. Legibility now comes from the pins and the seam, not from dentition.
- **EXCEPTION — Meridian keeps his current mouth.** He is the one unit Justin
  approved. His severity is the point.

## R9.2 — TRAVEL: much less. Smoother, fewer frames of motion.

*"Mouths open too much in the frames — the mouths don't need to open so wide,
which makes them smoother with less frames if they open less for speech."*

| frame | NEW gap @362 | (was Rev 8) |
|---|---|---|
| 0 | sealed, 0-4px seam | 0-8 |
| 1 | ~7px | 14 |
| 2 | ~12px | 24 |
| 3 | ~17px | 34 |
| 4 | **~22px max** | 40-45 |
A 22px opening on a 362px portrait is a speaking mouth. 45px is a yawn. Smaller
travel also means the frames blend more smoothly — that is the point.

## R9.3 — PER-UNIT EMOTIVE TARGETS (Justin's list, binding)

This is now the primary character spec. Everything — face geometry, posture,
glow, gear — serves the emotive read.

| Unit | Emotive target | Geometry that delivers it |
|---|---|---|
| **pulsar** | friendly, competent, helpful | open lifted brow, large round irises, gentle slight-up seam, no hard angles; the most welcoming face |
| **voyager** | battle-worn, experienced, friendly | heavy wear and burnishing, warm open brow, soft up-curved seam, crow's-foot panel lines at the eye corners; a veteran who's pleased to see you |
| **sentinel** | competent, intelligent, insightful, **smug** | ONE brow plate raised higher than the other (the smirk is in the brow asymmetry), a slight single-sided seam lift, crisp precise plates. Smug = knowing, not sneering |
| **nova** | tough, strong, serious, **deadpan** | *(CHANGED from eager/playful)* level brow, level seam, heavier squarer jaw plate, medium irises, planted stance. Zero smile. Deadpan is stillness, not scowling |
| **nebula** | creative, eccentric, joyful, contented | asymmetric or tilted crown element, softest fillets, clearly up-curved seam, wide bright irises; the happiest unit in the cast |
| **echo** | young, creative, swish, sleek, friendly | SLEEK — slimmer, more streamlined plates than Rev 8's chunky read; large irises, light up-curved seam, minimal bulk. Swish means elegant-fast, not cute |
| **iris** | smart, intelligent, creative, **angelic**, high-tech, friendly | the halo is the angelic cue — make it luminous and clean; refined slim plates, bright open irises, serene slight-up seam, the most *high-tech* finish in the cast |
| **atlas** | robotic, hardened, rough around the edges, stern, gets the job done | *(CHANGED from calm/neutral)* heaviest wear, chipped and scuffed plate, level-to-slightly-down brow, dead-level seam, blunt utilitarian forms. The least decorated unit |
| **meridian** | smug, deadpan, lawyer-like, doesn't care if others like him, serious | KEEP the approved face and mouth. Add a faint brow asymmetry for the smug read |

## R9.4 — NAMED FIXES

- **SENTINEL'S SECOND EYE.** *"Sentinel's second eye is looking off to the side
  which makes her look silly."* The scanner optic currently sits off-axis and
  reads as a wandering eye. **Both eyes must look FORWARD, parallel, at the
  viewer.** Mount the scanner optic coaxially in front of one eye or on a brow
  rail ABOVE the eye line — never beside it pointing away.
- **VOYAGER'S GOGGLES.** *"Voyager's goggles are still incomplete — it looks like
  the mouth area has been layered over it."* The goggle assembly must be a
  COMPLETE, continuous piece of hardware with an unbroken lower rim, sitting
  clearly ABOVE and SEPARATE from the mouth zone. Nothing overlaps or truncates
  it. (This is also §R8.13 clearance, failing in a new way.)
- **MERIDIAN'S GLOW + SCALES.** *"his current design is quite good but not enough
  glowing parts and the scales need to be more subtle like the glowing part of the
  other robots."* Add glowing accents to match the cast's powered-up level — lit
  seams in recesses, emitter beads, gorget lap glow. And **shrink the scales
  badge**: it currently dominates his chest. It should read like the other units'
  chest cores — a compact lit element, with the scales as a subtle motif WITHIN
  or OVER the glow, not a large brass ornament sitting on top of it.

## R9.5 — VOICE: each unit's own humour, or none (Justin)

*"Remove forced jokes and humour about not having hands etc — each one should have
their own style, their own humour... or lack of humour."*

The house tic (robot-can't-high-five, no-hands, circuits-malfunctioning) flattens
nine characters into one voice. **It is retired.** Each unit's spoken lines and
written voice follow its own register:

| Unit | Humour register |
|---|---|
| pulsar | warm, encouraging, lightly funny — the host who makes you feel capable |
| voyager | dry, understated, veteran's gallows humour — earned, never eager |
| sentinel | **smug**, precise, faintly amused at other people's mistakes |
| nova | **deadpan**. Flat statements of fact. The comedy, if any, is in what she doesn't say |
| nebula | eccentric, delighted, tangential — enthusiasm is her register |
| echo | quick, young, playful, a little slick |
| iris | bright, warm, articulate — clever rather than jokey |
| atlas | blunt, gruff, minimal. Doesn't do jokes. Reports and moves on |
| meridian | dry, smug, lawyerly — deadpan understatement, indifferent to approval |

No unit borrows another's register. **A drone that makes a generic robot joke is
off-character.** Applies to say.sh lines, review reports, and any written voice.

## R9.6 — GENDER READ follows the VOICE (Justin, 2026-07-31)

*"The ones that are using female voices, make the robot more feminine-looking and
those using male voices more masculine. Iris was a great example previously but now
she looks very androgynous. Nova can be a bit more androgynous by design."*

The Rev 8 machining pass flattened the cast toward androgyny — every unit got the
same heavy plate language. The voice and the face should agree: you hear Tessa, you
should be looking at something that reads feminine.

| Unit | Voice | Read |
|---|---|---|
| pulsar | Daniel (M) | masculine |
| voyager | Fred (M) | masculine, heaviest build |
| sentinel | Karen (F) | **feminine** |
| nova | Samantha (F) | **deliberately ANDROGYNOUS** — Justin's explicit call, and it suits her new tough/deadpan persona |
| nebula | Moira (F) | **feminine** |
| echo | Junior (M, boyish) | masculine, young — the smallest and slightest |
| iris | Tessa (F) | **feminine — the clearest in the cast.** She was right pre-Rev-8; restore it |
| atlas | Rishi (M) | masculine, broadest and most utilitarian |
| meridian | Ralph (M) | masculine, heaviest and most formal |

**HOW — proportion and form language, never anatomy.** The §D bans stand in full:
no eyelashes, lips, blush, bows, skirts, cinched or hourglass waists, breast-shaped
chest plating, hip flare, or hair-like cable styling. A robot has no anatomy to
simulate and simulating it is the cliché that makes this look cheap. The read comes
from **build**:

- **Feminine:** narrower jaw and chassis taper, a slimmer neck column, smaller
  shoulder-to-head ratio, more refined and slender plate edges, more curvature and
  fillet in the forms, lighter overall mass, finer detailing, more elegant
  proportions. Think a precision instrument rather than a bulldozer.
- **Masculine:** broader jaw, wider shoulder-to-head ratio, heavier plate, blunter
  and squarer forms, more mass and visible structure, coarser fasteners.
- **Androgynous (Nova only):** deliberately mid on every axis — neither taper nor
  bulk, balanced shoulder ratio, forms that don't commit either way.

**Reference for Iris:** `design/drones/before/iris.png` and
`design/drones/pre-rev8/iris.png` — she read clearly feminine there through
proportion and refinement alone. Get that back on top of the Rev 9 machined face,
without reintroducing a single banned cue.
