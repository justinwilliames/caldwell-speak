# SPEC-R1 — Atlas (UX / first-principles) review of FACTORY-STYLE.md

## Verdict
Directionally right but under-specified for the actual job. The eight rules solve
"look like one factory" and say almost nothing about "stay tellable-apart at 52px" —
and the two goals pull against each other more than the spec admits. Ship it with the
additions below, not as-is.

## 1. Consistency vs distinctness — where it breaks, and the fix
The current cast's flaw isn't lack of shared materials — it's that Sentinel/Nova/
Nebula/Pulsar/Echo/Atlas/Iris/Meridian already look like one mold (same black-visor
rectangle, same round flat-glow eyes) with color as the only real signal. Rules 1, 3,
4, 5 (chassis material, eye construction, mouth construction, helmet construction)
are exactly the elements that are ALREADY identical across the cast. Applying them
literally and uniformly recreates the same-mold problem in gunmetal instead of white
plastic — nine Voyagers in different paint.

**Resolution — make these explicit "must vary" axes, not just "preserve accessories":**
- **Eye glow colour = registry hex, full saturation, and it is the PRIMARY signal.**
  State this explicitly (it currently isn't — rule 3 talks about lens/pupil/catchlight
  construction but never pins the glow colour to identity). Never mute it for realism.
- **Helmet/head silhouette must differ by drone**, not just the face inside it — Echo's
  dish, Iris's halo, Atlas's antennae change the OUTER contour, which reads at
  thumbnail when nothing else does. Rule 5 ("rounded helmet dome... brow band, ear
  pods") should say "this is the shared construction *language*, not a shared
  silhouette" or every dome converges to the same rounded shape again.
- **Wear/edge-treatment is a legibility variable, not just flavour text.** The identity
  table already varies this (sentinel "minimal wear," echo "least wear") — promote it
  to a first-class rule alongside the eight, because applying Voyager's weathering
  uniformly is the fastest way to also flatten age/gender read across the cast (see §3).

## 2. Thumbnail survivability, rule by rule
| Rule | Survives at 52px? |
|---|---|
| 1 micro-wear/rivets/vents | **No.** Sub-pixel at 52px, barely visible at 125px. Spend zero effort here beyond "reads as metal, not plastic" from a distance. |
| 2 metal accent trim | **Partial.** Only if the trim is a large, saturated, distinctly-placed shape (visor rim, chest badge) — fine anodised detail vanishes. |
| 3 eyes (ring+pupil+catchlight+lens) | **Partial.** Ring colour + rough pupil position survive; lens reflections/glare are noise at this size — keep them subtle or they degrade contrast. |
| 4 lit mouth w/ interior depth | **Partial.** Reads as "a warm line," the depth doesn't. Fine — cheap to add, costs nothing to keep. |
| 5 helmet construction (seams/fasteners/brow band) | **No** for the fine detail; **yes** for gross shape/silhouette (see §1). |
| 6 navy background | **Yes**, and free — shared background helps grouping without competing with identity. Keep. |
| 7 warm rim-light + DOF | **Partial.** Directional highlight can help silhouette pop; falls apart if it's inconsistent across colours. Low priority, don't over-invest. |
| 8 tight hero framing | **Yes**, cheap, and load-bearing for accessory silhouette (antennae/halo/dish need to survive the crop). |

**Net: detail budget should go to (a) eye colour saturation, (b) outer silhouette
accessories, (c) framing/crop — not to rivets, seams, or micro-wear, which are
render effort spent on something nobody will ever see below "click to enlarge."**

## 3. Voice-match section — actionability critique
Not checkable as written. Rows mix concrete, measurable cues ("narrower jaw/chassis,"
"heavier shoulders," "larger eyes relative to face") with pure adjectives ("poised
and welcoming," "confident bearing," "poised conductor") that eight independent
generations will interpret eight different ways. The negative list (no eyelashes/
lips/blush/bows/skirts) guards against the worst cliché but gives no positive target,
and image models under-specified on "feminine" reliably reach for exactly that
cliché list by default — this section is likely to produce a result Justin rejects
on sight for Sentinel/Nova/Nebula/Iris specifically, via reflexive slimming +
pink-shift, not because a builder chose it but because it's the model's prior.

**Fix:** replace the adjective column with a 4-axis ordinal rubric per drone —
jaw-width (narrow/med/wide), eye-size-ratio (small/med/large), wear-level
(none/light/mod/heavy — already half-exists), edge-treatment (soft-rounded/sharp).
Ordinals are falsifiable in a way "elegant proportions" isn't; a reviewer can check
the output against 4 numbers instead of a vibe.

## 4. What's missing
- **No thumbnail acceptance gate.** Step 2 of the playbook judges against the 8 rules,
  identity, and framing — never against "can someone identify this drone blind, at
  52px, in under a second." That's the actual definition of done and it's absent.
- **No pairwise confusability check.** Azure/teal/green (sentinel/echo/nova) and grape/
  indigo/magenta (atlas/pulsar/nebula) are hue-adjacent clusters — the spec should
  require rendering confusable pairs side-by-side at 52px before sign-off.
- **No colour-blind-safe check** — the whole system leans on hue; ~8% of male users
  have red-green CVD and the palette hasn't been screened at all.
- **No regression test against the old cast** — nothing confirms the new render is
  *more* legible than today's, only that the nine match each other.

— Atlas
