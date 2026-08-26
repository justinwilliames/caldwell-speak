---
name: drone-forge
description: End-to-end creation of Pulsar drone characters — design brief, image generation, registration, automated gates, team review, voice casting and provenance. Trigger on "new drone", "add a drone", "redesign a character", "regenerate the cast", "the portraits look wrong", "change <drone>'s face/voice/uniform", "cast a voice", or any request to create or alter drone art. Carries the locked taxonomy, the full pipeline, the gate suite, and the rulings that were paid for in rework. Do NOT use for lip-sync frame sets (a separate pipeline) or for app UI work.
---

# Drone Forge

> Making a Pulsar drone look right is not a prompting problem. It is a **pipeline with
> gates**. Every property that matters — framing, pose, hue, glow, background — has been
> instructed in prose, confirmed by eye, and then measured to be wrong. Prompt what the
> character *is*; **gate** everything you can count.

---

## 0. The one rule that saves the most time

**Prompts do not hold. Gates hold.**

Measured, repeatedly, on this cast:

| Property | Instructed | Actually rendered |
|---|---|---|
| Head size in frame | "about 28% of image width" | 39.6–51.4% |
| Brand hue | locked hex, ±20° tolerance | Nebula 30.5° off |
| Glow | "consistent across the cast" | 18× spread, later 134× |
| Chest orb | "THERE IS NO CHEST ORB" | rendered on 7 of 9 |
| Head pose | "dead-on, passport photograph" | up to 21° of yaw |

So: put character, materials and personality in the prompt. Put anything countable in
`scripts/cast-gate.py`, and let `scripts/cast-build.py` loop until it passes.

---

## 0b. End to end, in order

1. **Decide what is locked** — role, brand hex, Kokoro voice (§2). Accent and gender follow
   the voice id; everything else is authored.
2. **Write the brief** into `JOBS` in `cast-generate.py` (§3b).
3. **Generate and gate in a loop** — `cast-build.py` (§1).
4. **Review with `pulsar-team`**, cross-assigned, with authority to block and to author new
   gates (§6).
5. **Cast the voice** and confirm it against the face (§6b).
6. **Record provenance** — archive, stamp, manifest (§8).
7. **Freeze the master and build the frame sets** — six registered frames per drone (§7).

## 1. The pipeline

```bash
python3 scripts/cast-build.py                  # generate → gate → re-render failures → repeat
python3 scripts/cast-build.py --only nova      # one character
python3 scripts/cast-gate.py v8                # just measure
```

Underneath, in order:

| Script | Job |
|---|---|
| `cast-generate.py` | one brief per character; **prompts live here** |
| `cast-align.py` | registers on MediaPipe iris centres, crown-anchored |
| `cast-provenance.py` | archives true-format masters, stamps AI metadata |
| `cast-gate.py` | measures every countable property, exits non-zero |
| `cast-manifest.py` | hashes each asset and the prompt that made it |
| `cast_pose.py` | true yaw/pitch/roll from the 478-point face mesh |
| `cast-lint.py` | **spec parity** — every brief held to the same standard, before generation |
| `cast_checks/` | team-authored gate plugins, auto-loaded |

`cast-build.py` re-renders **only** the failures, injecting a correction keyed to the
specific check that failed. Corrections **accumulate** — see §5.

**`cast-lint.py` runs first and can stop the build.** The image gate polices renders; the
lint polices *specs*, because quality slipped in the brief long before it showed in a
picture — one drone carried a 2,112-word brief while another carried 552, and the thin one
rendered generic. It enforces ten required sections per character, a word floor, distinct
roles, distinct modification sites, and no brief still quoting a repealed rule. **Match its
section patterns case-insensitively** — the briefs shout their headers and a case-sensitive
pattern silently reports a section missing that is plainly there.

### 3b. Prompt architecture

`cast-generate.py` assembles each prompt from shared blocks plus one per-character brief:

```
REGISTER   the world: photoreal, futurist-meets-steampunk, materials, what is banned
LAWS       numbered rules that apply to all nine (glow, mouth clearance, machine tell)
UNIFORM    the one garment, its two cuts, and what gear layers over it
FRAMING    pose, crop, background
+ per-character brief: fixed identity · physique · face · hair · expression ·
  ONE piece of profession hardware · groove language · where the colour sits
```

Two reference images are passed with every call:
- **Image 1 — the style anchor.** Pulsar, generated first with no anchor, then used as the
  anchor for the other eight. This is what holds the cast together; without it nine
  independent renders drift into nine unrelated illustrations.
- **Image 2 — the character's own prior master**, for lineage. Carry colour, emblem and
  silhouette cues across; never its literal shape.

Write briefs as **what IS there**, not what is absent. A list of bans ("no orb, no lamp, no
emitter") reliably produces the banned thing; describing plain unbroken fabric does not.

---

## 2. What is locked

From `macos/Pulsar/Sources/Models/DroneRegistry.swift` and the Kokoro voice map. Do not
change these while designing art; changing them is a separate, deliberate decision.

| Drone | Role | Hex | Kokoro voice | Reads as |
|---|---|---|---|---|
| pulsar | Chief of Staff | `#818CF8` | `bm_daniel` | British male |
| voyager | Data Engineer | `#F2A83B` | `am_onyx` | American male |
| sentinel | Data Analyst | `#6BB8EB` | `af_sarah` | American female |
| nova | Software Engineer | `#5CD16B` | `bf_alice` | British/Irish female |
| nebula | Graphic Designer | `#E85CD1` | `bf_emma` | British female |
| echo | Copywriter | `#2EBFB8` | `am_puck` | American male |
| atlas | IT Support | `#8040C0` | `am_fenrir` | American male |
| iris | Marketing Manager | `#F26178` | `af_heart` | American female |
| meridian | General Counsel | `#24427A` | `bm_george` | British male |

**A Kokoro voice id encodes accent and gender ONLY** — first letter `a`/`b` for American or
British, second `f`/`m`. There is **no ethnicity metadata**. Any ethnicity in a character is
an authored choice, not a fact the data supplies. Say so rather than presenting it as locked.

**Known palette tension:** `meridian`'s navy has the lowest luminance in the cast by 26% and
cannot pass a glow floor at any brightness. That is a palette decision, not a render defect —
escalate it rather than regenerating him.

---

## 3. The design standard

**Register:** futurist meets steampunk. Aged brass and copper against gunmetal; exposed
rivets, knurled collars, small gears, gauges, compression fittings. *Modern light, antique
engineering.* Photoreal. The Expanse for materials — used, worked, issued, repaired.

**Uniform:** ONE garment on all nine — charcoal `#23262B`, high collar, raked yoke seam,
brand-colour piping. Two cuts (masculine/feminine), same garment. What varies is the **gear
layered over it**: heavy field kit (Voyager, Nova, Atlas), light working kit (Nebula, Echo),
nothing added for the executives (Pulsar, Sentinel, Iris, Meridian).

**Android read:** glowing irises are the primary tell — glow in the **iris ring**, pupil stays
a dark hole. Machined panel seams on the face, lit in the character's colour. Hardware is
**grafted** into the body wherever plausible (socketed into the skull, bolted to the mandible,
flesh sealed with a healed margin), not worn.

**Framing:** dead-on to camera, head and shoulders, near-black background with the character's
colour hazing behind. A coloured glow flooding the frame is fine; **scenery is not**.

**Sacred:** nothing crosses the lips, jaw hinge or chin — these become lip-sync frames.

---

## 3c. Colour — use the published palette, never a hand-picked hex

`drone-forge/palette.json` holds Sasha Trubetskoy's *20 Simple, Distinct Colors*, supplied by
Justin on 2026-08-13. **It is the colour source.** Ten are in use; ten are reserve for drones
11–20.

Hand-picking per-character hexes failed twice, in the same way both times: the cast drifted
into **three drones inside a 30° wedge of blue** (sentinel 204°, meridian 219°, pulsar 234°)
and **two inside 17° of red** (vector 8°, iris 350°). A set designed for mutual distinctness
removes the failure mode rather than policing it.

**Measure hue, not just ΔE.** This is the ruling that cost the most. The cast rule was
CIE Lab ΔE76 ≥ 40, and it passed both collisions — sentinel vs meridian at ΔE 47.6, iris vs
vector at 46.5 — because ΔE weighs lightness heavily and those pairs differ in lightness while
sharing a hue. A human reads them as one colour, lighter and darker. **Gate both:** ΔE for
overall separation, hue angle for colour-family separation.

**Assigning the palette:** minimise total hue rotation from each character's existing identity,
so nobody's look changes more than it has to, and **pin any character whose colour is
load-bearing** — Pulsar carries the app's own brand blue and does not move. Never assign in
list order; the list is not ranked.

**Do not bolt a second separation metric onto the palette.** I tried forcing flagged pairs ≥45°
apart in hue before assigning; it simply moved the collision onto a different pair each run, and
a self-check found *five* pairs inside the palette itself failing that rule. Strong red and
light pink sit 15° apart and are obviously different colours — they differ by 36 points of
lightness. The palette already encodes distinctness across hue *and* lightness; second-guessing
it with a hue-only rule is fighting the premise. Judge a pair on both, and never reject a
published-palette pair for failing a test it was never designed to pass.

---

## 4. Adding a new drone

1. Add it to `DroneRegistry.swift` with a colour at **ΔE76 ≥ 40** from every sibling. The
   cast's tightest existing pair sits at 34 and is visibly confusable — 34 is not enough.
2. Pick a Kokoro voice from `VoiceDownloader.availableVoices`; let its prefix set accent and
   gender, then author the face to match.
3. Add a brief to `JOBS` in `cast-generate.py`. Copy the nearest sibling's structure: fixed
   identity, physique, hair, expression, the **one** piece of profession hardware, the groove
   language, and where the colour sits.
4. Give it a **distinct colour-carrier and mod site** — no two units wear their colour the
   same way or carry hardware in the same place. That is what stops nine faces converging.
5. Add its slug to `CAST` in `cast-gate.py`, `cast-align.py`, `cast-build.py`, `cast_pose.py`.
6. Run `cast-build.py --only <slug>` until it passes, then a full-cast gate.
7. Add the slug to `CAST` in `cast-lint.py` and `cast-manifest.py` too, and run
   `python3 scripts/cast-lint.py` — the new brief must reach the same standard as the
   incumbents before a single pixel is generated. A short brief is the cheapest defect
   to fix and the most expensive to notice later.
8. Seat it in `pulsar-team`'s roster (§1.x) with its own scar, instruments, failure mode
   and boundaries against the two nearest lenses — and raise the documented cast cap. A
   drone that reviews without a lens of its own just agrees with the room.
9. Run `pulsar-team` for sign-off (§6).

---

## 5. Rulings paid for in rework

Each of these cost a full regeneration cycle or worse.

- **Never strip correction text with a file-wide regex.** `re.sub` on a pattern like
  `LIGHTING FAILURE...(?:\n(?!\n)[^\n]*)*\n` runs past the paragraph it meant to remove,
  because the next non-blank lines are `=== END CORRECTION ===` and the block's own
  closing `"""),`. Eating those merges two characters into one and, on the last entry,
  deletes a whole drone — it removed Vector outright and left Pulsar unterminated, and
  the build then died minutes later with `ValueError: substring not found`, far from the
  cause. Use `scripts/cast-strip-corrections.py`: it cuts on the character's own start
  marker and the next character's start marker, re-asserts the closing delimiter rather
  than assuming it survived, and refuses to write unless the result still parses and
  still holds every brief. **A recovered brief is recoverable from the session
  transcript** (`~/.claude/projects/*/<session>.jsonl`) when the file is the only copy.

- **A correction outliving its check is a defect.** Two separate rounds were lost to
  this. The anti-orb correction kept injecting a rule the gate had stopped enforcing,
  and `brief_drift` then correctly failed the brief for obeying a repealed law. Worse,
  `brief_drift` decides "repealed" by matching correction keys against the failure
  strings the pipeline can emit — and it only harvested literals returned *inline*, so
  `legible64`, which writes `msg = f"converges with ..."` and returns the variable,
  looked repealed and failed every brief carrying its correction. Harvest assignments
  too. **When a check is retired, delete its correction in the same edit.**

- **Every failing check needs a correction, or the loop cannot converge.** Half the
  team-authored plugins had no entry in `CORRECTIONS`, so the build re-rendered those
  failures with nothing new to say and spun. Collision corrections must also NAME the
  sibling — "differ from another character" is not an instruction; "differ from Meridian"
  is.

- **Comparative checks must judge against a FIXED target, not the cast's live median.**
  `headsz` compared each head to the median of the current cast, so re-rendering the
  failures moved the goalposts for everyone else: Atlas passed a round, was not
  re-rendered, and failed the next one purely because its siblings moved. With ten
  characters and several pairwise checks, that oscillation never settles. Pin the target
  to the value measured when the framing was signed off.

- **Check that the correction and the brief agree on direction.** The lighting law says
  key from *frame* upper-left and the gate measures image-left brightness, but the
  correction said "the character's left (the viewer's right)" — the opposite side. It
  drove three drones to fail the very check it was written to fix.

- **Splice by explicit boundary, never by "the next entry I remember."** Cutting from
  `("pulsar"` to `("nova"` silently deleted Voyager and Sentinel; the symptom was
  `generated 0` with no error.
- **Corrections must accumulate.** Replacing a character's correction block each round with
  only its current failures makes defects oscillate: a fixed orb regrows the moment its
  instruction is dropped. The loop stalls and never converges.
- **Never delete a check when a rule changes — invert it.** When the orb was cut, disabling
  the core check let a cast still wearing orbs pass 9/9. A rule with no check is a comment.
- **A "missing" element is usually a cropping failure.** Chest cores were declared missing
  and prompted six ways; they were rendered correctly all along at 87–92% down the frame and
  the crop was slicing them. Measure the raw master before blaming the model.
- **Verify a detector before trusting its verdict.** Drawing the measured iris line onto the
  portraits showed it pairing an iris with a *headset highlight*, condemning two characters
  who were square to camera. Overlay the measurement on the image.
- **Do not verify a transform with the detector that computed it.** Self-confirming
  registration passed a character whose head was 28% undersized.
- **Round and centred, not merely largest.** "Biggest lit blob in the chest band" passed
  shoulder piping and collar edges as chest cores on 8 of 9.
- **`.capitalized` mangles real job titles** — "IT Support" becomes "It Support".
- **Gemini returns JPEG bytes.** Writing them to `.png` filenames makes lossy, mislabelled
  masters whose C2PA credential no PNG re-encode can carry.
- **`GEMINI_API_KEY` lives in `~/.zshrc`**, so only an *interactive* zsh sees it. A stale
  `<your-key>` placeholder export shadows the real key and turns every call into a silent
  HTTP 400 — the build ran four full rounds and regenerated nothing.
- **Photoreal + a described minor trips `IMAGE_SAFETY`.** Age the character into their
  twenties and drop "boyish"-type phrasing.
- **The model will not stop rendering a chest orb** no matter how absolutely it is banned.
  Describe what *is* there (plain unbroken fabric) rather than listing absences.

---

### The standard-bearers

Seven characters were signed off on 2026-08-13 — Pulsar, Voyager, Nova, Nebula, Atlas, Iris,
Meridian — and `STANDARD` in `cast-build.py` names them. They are **not frozen**: name one with
`--only <slug>` and it re-renders, which is how a deliberate tweak is made. What they are
protected from is the INCIDENTAL re-roll. The generator takes no seed, so an automatic
re-render rolls a brand-new face and destroys the approved one. When a comparative check flags
a standard-bearer, that is a fact about the sibling that moved — **the sibling moves back, not
the standard.**

### Framing is fixed by one character, not by a committee

The aligner used to pick ONE GLOBAL SCALE — the tightest that kept every crown in frame — so
the tallest headgear in the cast dictated the zoom for all ten, and each output inherited
whatever head size the generator happened to produce (IOD spanned 12.3%–17.7%). Vertical
placement was crown-anchored, so the eye line rode with hair height (32.9%–42.6%).

Both are wrong for a cast that has to look like one shoot. Pick the character whose framing is
right, measure it, and normalise everyone to it — per-character scale to a fixed IOD, and
eye-anchored vertical so faces sit at the same height. The cost is the top of a tall hood or a
big haircut, which is the cheaper thing to lose. Voyager is the current reference:
`IOD, EYE_CY = 0.166, 0.366`.

- **A hardcoded roster in a build script is a silent-failure generator.** The tenth drone's
  six frame assets were declared in neither `build-pulsar-app.sh`'s copy list nor
  `Package.swift`'s `resources:` block. The app built clean, installed clean, reported
  success — and shipped 54 of 60 assets with one drone that could not open its mouth.
  The build script now enumerates by glob, `Package.swift` is checked against
  `DroneRegistry.swift` by a guard that **exits non-zero** naming the missing files, and
  the guard was proven by deleting a declaration and watching it fire. SPM cannot glob
  resources, so that list stays hand-written — which is exactly why it needs a guard.

- **The lineage reference will fight a colour change and win.** Each render is given the
  character's previous portrait with the instruction "carry its colour and emblem across".
  When the cast moved to a new palette, that instruction was pointing at the OLD colour, so
  four drones kept rendering their old hue no matter what the brief said. Lineage is for
  FACIAL IDENTITY; state explicitly that the locked colour replaces whatever the reference
  shows.

- **Put the locked colour IN the spec hash.** `brief_hash()` captured the brief text but
  not the hex, so a palette change did not register as a spec change and the ratchet rolled
  eight characters back to their old colours while reporting success. A defect that reads
  as *nothing happening* is the worst kind.

- **One source of truth for colour, or the copies will agree with each other.** The palette
  was hardcoded in `cast-gate.py` AND `cast-align.py`. Both were left behind by the palette
  change, so `hue_fid` gated every drone against a hex that existed nowhere else and passed.
  Sentinel and Voyager found it independently in the same review — which is how you know it
  was invisible rather than unlikely. Both now load `drone-forge/current-assignment.json`.

- **Register frames with an AFFINE pyramid, not a Euclidean single pass.** Euclidean models
  rotation and translation only, so a cell rendered at a slightly different head SIZE has no
  parameter to absorb it: the first frame batch left 5.3px and 8.8px of drift with 9-16% of
  the upper face moving. Affine adds scale; a three-level coarse-to-fine pyramid converges
  from a far worse start. Same sheets, re-registered: drift fell to ≤1.1px and every
  character passed. **Keep the sheets on disk** and re-cut them (`--reuse-sheets`) — the
  generation is the expensive part and the registration is the part you iterate.

- **Read a brief back against itself.** Nova's mandated a grinding shield and then twice
  banned face shields, so she grew goggles that duplicated Voyager's; Nebula's mandated a
  colour-calibration loupe and then said "REMOVE THE EYE LOUPE ENTIRELY — no eyepiece of any
  kind", leaving her with NO profession hardware and a lit-elements line citing an indicator
  bead that no longer existed. `cast-lint.py` now flags any kit noun that is both mandated
  and forbidden. Count **mandates, not mentions** — a brief legitimately narrates its own
  history, and counting that as a requirement made the check cry wolf on four nouns at once.

## 6. Sign-off

Run `pulsar-team` and give the drones real authority — SHIP / SHIP WITH CAVEAT / BLOCK.

**Cross-assign the reviews so no drone audits its own portrait.** Self-review produced
flattery; cross-assignment produced the three findings that mattered most.

They may also **author gates**. Any module in `scripts/cast_checks/` exposing `NAME` and
`check(img, path, rgb) -> (value, ok, message)` is auto-loaded and runs against all nine. A
check must **discriminate** — demonstrate it passing one character and failing another with
quoted output — and must measure the property itself rather than a proxy. See
`scripts/cast_checks/README.md`.

The team has caught the gate measuring the wrong thing three separate times. **Their block is
worth more than the gate's pass.**

### Gates the team has authored

| Check | Measures | Why it exists |
|---|---|---|
| `hue_fid` | rendered accent vs the locked hex | a character rendered 32° off its own colour and nothing caught it |
| `xreg` | two independent registration routes agreeing | the aligner used to verify itself with the detector that computed the transform |
| `legible64` | pairwise thumbnail distance at 48px | two characters can converge at menu-bar size while looking distinct at full res |
| `individuation` | face-mesh geometry distance between characters | catches two faces converging, the opposite failure to cast incoherence |
| `keylight` | key-to-fill ratio and lighting direction | nine portraits lit differently do not read as one authored set |
| `brief_drift` | brief still enforcing a repealed rule | a cast wearing orbs passed a gate that claimed they were cut |
| `lineage` | derived asset actually derives from its named master | catches stale aligned frames after a regeneration |

### The robot/human balance — 60/40, and why it is written down

The cast reads as **60% machine, 40% biological**. Concretely: the skull, jaw, temples,
cheek structure, neck and shoulders are manufactured; what stays biological is the face
proper — eyes, nose, mouth and lips, cheeks — and the boundary between the two is crisp
and visible. At a glance the viewer sees a robot, and only then notices the face is alive.

This is written as a proportion rather than a mood because "more robotic" drifted every
regeneration. Ask for a machine with biological parts, not a person with implants: the
second phrasing produced faces that were 90% human with a seam drawn on.

### 6b. Voice casting

Voices are Kokoro, rendered on-device. To audition them honestly, **speak through the running
app and capture the real audio** rather than substituting `say`:

- The app records `id`, `voice` and `text` per line at `GET /history` (token at
  `~/.pulsar/daemon-token`, header `X-Pulsar-Token`), and caches audio as
  `cache/history/<id>.mp3`.
- **Map by id, never by file timestamp.** Timestamp-matching silently mis-assigns clips when
  another session speaks into the shared queue — five of nine were wrong that way, and the
  error is invisible until someone listens.
- Extra voices can be fetched from `VoiceDownloader.availableVoices` into the app's voices
  directory; `say.sh --voice <id>` does **not** currently drive Kokoro voice selection, so
  auditioning a non-cast voice means editing the drone map.
- A casting artifact (portrait + play button per character) is the fastest way to get a
  verdict. Verify each clip against the history record before publishing it.

---

## 7. The frame build — only once the masters are signed off

The portrait is not the deliverable. **Nine drones × six frames** is: five mouth positions
plus a blink, which `PortraitView.swift` crossfades by audio amplitude.

### The naming contract, which the app depends on

```
macos/Pulsar/Sources/Resources/<category>-mouth-0.png   closed / rest
                              <category>-mouth-1.png    ↓
                              <category>-mouth-2.png    ↓ opening
                              <category>-mouth-3.png    ↓
                              <category>-mouth-4.png   full open
                              <category>-blink.png      eyes closed, mouth at rest
```

362px, and `PortraitView.swift` hard-checks `frames.count == 5`. Changing the count or the
naming means changing the loader too — do not do one without the other.

### The rule that governs everything here

**Derive all six frames from ONE approved master. Never generate them independently.**

Two independent generations of the same character drifted **+7px crown, −29px centre, +6.0%
scale**. At that drift the face swims while the mouth moves and the effect is unusable. The
model takes no seed, so independent renders can never register.

### Method

1. **Freeze the master.** The gate passes, the team signs off, the manifest is written. Any
   later change to the master invalidates every frame derived from it — `lineage` in
   `cast_checks/` catches this.
2. **Generate a 3×2 sprite sheet** from the approved master in a single call — six cells,
   one image, so all six share lighting, pose and identity by construction.
3. **Crop the cells**, then register each against `mouth-0` with OpenCV
   `findTransformECC` (`MOTION_EUCLIDEAN`), and downsample to 362px.
4. **Verify registration**: phase-correlate every frame against its own `mouth-0`. Anything
   other than `(0,0)` is drift and must be re-registered, not shipped.

### Definition of done, and it is measurable

For each character, comparing `mouth-0` against `mouth-4` at one named threshold:

- **forehead + eyes move < 3% of pixels** — the face is still
- **mouth + jaw move ≥ 8% of pixels** — the mouth actually opens

Both must hold. This is the condition that separates a talking face from a flapping decal,
and it is why the earlier robot cast failed: its full open-to-closed travel was **19 of 362
rows, 5.2% of head height**, against a human jaw drop of 15–20%.

### Visemes, if the mouth is ever driven by phonemes

Amplitude-driven lip sync picks a frame from loudness alone, so "ee" and "oo" at the same
volume get the same mouth. Kokoro's pipeline returns an IPA phoneme string, which makes real
visemes possible. If that path is taken, generate **seven shapes** — `rest, MBP, FV, EE, L,
OO, AA` — and let amplitude mode drive the ordered subset `rest → EE → L → AA`. Same art
serves both, so the asset structure should not hard-code "5 frames indexed by loudness".

### Frame-level gates worth having

- every frame present for every character, correct names, correct size
- phase correlation `(0,0)` against `mouth-0` for all six
- the still/moving pixel-share test above
- nothing crossing the lips, jaw hinge or chin in any frame

---

## 8. Provenance — non-negotiable

Renders carry a signed C2PA manifest and SynthID watermark; re-encoding destroys them.
`cast-provenance.py` archives byte-identical masters under their true extension to
`generated-images/masters-archive/` and stamps derived PNGs with `tEXt` provenance.
`design/drones/PROVENANCE.md` must state **method, not warranty** — what ran, what was
instructed, what was checked, and explicitly what was **not** (no likeness clearance has been
run; record that as inability to exclude, never as clearance). The model takes no seed, so
nothing is reproducible: `cast-manifest.py` hashing every asset and prompt is the
accountability mechanism that replaces reproducibility.

---

## Sync home

Canonical: `~/code/pulsar/drone-forge`. Copy to `~/.claude/skills/drone-forge` after edits,
alongside the `pulsar` and `pulsar-team` pair.
