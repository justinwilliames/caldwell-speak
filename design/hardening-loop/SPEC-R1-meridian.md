# Spec Review — Round 1 — Meridian (General Counsel)

**Scope:** `/Users/justin/code/pulsar/design/FACTORY-STYLE.md` — nine AI-generated robot
portraits, public MIT repo + app bundle. This is a review-level read for an internal
build spec, not formal legal advice — flagging where I'd want a lawyer's eyes if this
were higher-stakes, but nothing here needs one.

## Verdict

Ship-able after one wording fix. The spec's instinct is already mostly right — it
explicitly bans the laziest gendering tells (eyelashes/lips/blush/bows/skirts) and
frames gender as "proportion, not costume." But the ban list misses the failure mode
an image model is actually most likely to produce, and the "feminine/masculine"
labels are doing no design work the character language underneath them isn't already
doing — so they're pure downside with no upside.

## 1. Gender-depiction instruction

**Risk:** the ban list (eyelashes, lips, blush, bows, skirts) blocks the obvious,
laziest tells — a diffusion model isn't likely to add a skirt to a "matte gunmetal
factory robot" prompt anyway. What it's likely to do, unprompted, when told
"feminine": taper the chassis into an hourglass, add breast-shaped chest plating, add
hip flare, or turn an antenna/cable into hair. That's the actual stereotype-caricature
risk on a public repo, and the spec doesn't name it.

**Exact replacement wording** (extend the closing sentence of "How to express gender
without cliché"):

> NOT via eyelashes, lips, blush, bows, skirts, cinched or hourglass waists,
> breast-shaped chest plating, hip flare, hair-like cable/antenna styling, or any
> simulated human secondary-sex characteristic or gendered costume. A feminine- or
> masculine-coded build differs in proportion and bearing only — jaw width,
> shoulder-to-head ratio, chassis taper, scale, brow shape — never in simulated
> anatomy.

That's the right ban *plus* this addition — the existing five items stay (cheap,
harmless to keep), the anatomy items are the ones that actually needed saying.

## 2. Is the framing sound — my one recommended position

**Reframe to character, drop the gender label.** Look at the table: three entries
already do this correctly without the word "feminine/masculine" doing anything —
voyager ("gruff retro rasp" → older, weathered), echo ("light boyish" → youngest,
least wear), meridian ("deep slow measured" → senior, composed, still). All three are
age/gravitas cues, not gender cues, and they're the least risky rows in the table.

The other five rows (sentinel, nova, nebula, iris, atlas) attach "feminine"/"masculine"
as a label, but the actual instruction to the generator is already a character
attribute wearing that label: "crisp en-AU, precise and clipped" is a *precision* cue,
not a femaleness cue; "broad and grounded, calm" is a *gravitas* cue, not a maleness
cue. Dropping the label loses nothing — the resulting silhouette cues (narrower
jaw, rounder/brighter, curved forms, elegant proportions, broad shoulders) are
unchanged and a viewer will still read a felt gender from proportion alone if that's
what lands. What the label adds is pure risk: a downstream builder reads "feminine"
as license for stereotype shorthand, and a public README that states robots have a
gender is a stranger claim than one that says a robot's *build reads as* precise,
warm, youthful, or grounded. Recommend: rename the column "Voice character" and
replace "feminine, X" / "masculine, X" cell text with the character words already
present (precise/clipped, bright/energetic, warm/flowing, poised/welcoming,
broad/grounded) minus the gender adjective.

## 3. AI-asset provenance

Record at generation time, per drone, in a lightweight `design/drones/PROVENANCE.md`
or sidecar: **model** (codex-imagegen + underlying model/version), **full prompt
text**, **reference images used** (both the drone's prior master and voyager.png, by
filename), **date**, and a one-line attestation: "no real-person likeness; not
modeled on a third-party copyrighted character design."

The prior masters and voyager.png being the project's **own** earlier AI-generated
assets does change one thing and not another: it removes third-party rights-chain
risk for the *style reference itself* (nothing scraped, nothing else's IP entering
via the reference), but it does **not** remove the need for the record — the
answerable question isn't "did we have rights to the reference," it's "does this
output resemble a known copyrighted robot," which is orthogonal to where the
reference came from.

## 4. Other exposure

- **Add a fourth review check at spec step 2**: "(d) not a recognizable likeness of
  an existing copyrighted robot/character design" — cheap to add, closes the one real
  IP-adjacent gap in a public MIT distribution.
- **One-line AI-generation disclosure** in the README near the portraits — low cost,
  gets ahead of AI-content-labeling norms/rules that are tightening globally.
- MIT covers the code; if anyone ever asks, worth one sentence stating the license
  posture for the art assets themselves (MIT extends to them here, but projects
  sometimes carve out art separately — just state the position once).

— Meridian
