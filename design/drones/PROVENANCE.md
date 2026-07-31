# Character art provenance

All nine Pulsar character portraits and their lip-sync frame sets are
**AI-generated**, produced 2026-07-30/31 via `codex-imagegen`, most recently the **Rev 9** pass (small machined-seam mouths, per-unit emotive targets, gender read by proportion, raised glow) (OpenAI Codex CLI
image generation) driven by prompts authored in this repository.

**Attestation, applying to every asset listed below:** no real-person likeness;
not modelled on a third-party copyrighted character.

## Method

Each master was generated image-to-image from the project's **own prior master**
for that character (never a third-party image, and never another artist's work),
under the house standard recorded in `design/FACTORY-STYLE.md`. Reference images
used are therefore all previously-generated assets from this same repository, so
there is no external rights chain in the inputs.

Lip-sync frames were generated as a 3x2 sprite sheet per character (six 512px
cells) from the approved master, cropped, then registered with OpenCV
`findTransformECC` (MOTION_EUCLIDEAN) and downsampled to 362px.

## Assets

| Character | Master | Frames |
|---|---|---|
| voyager | `design/drones/voyager.png` | `voyager-mouth-0..4`, `voyager-blink` |
| sentinel | `design/drones/sentinel.png` | `sentinel-mouth-0..4`, `sentinel-blink` |
| nova | `design/drones/nova.png` | `nova-mouth-0..4`, `nova-blink` |
| nebula | `design/drones/nebula.png` | `nebula-mouth-0..4`, `nebula-blink` |
| echo | `design/drones/echo.png` | `echo-mouth-0..4`, `echo-blink` |
| iris | `design/drones/iris.png` | `iris-mouth-0..4`, `iris-blink` |
| atlas | `design/drones/atlas.png` | `atlas-mouth-0..4`, `atlas-blink` |
| meridian | `design/drones/meridian.png` | `meridian-mouth-0..4`, `meridian-blink` |
| pulsar | `assets/readme/pulsar.png` | `pulsar-mouth-0..4`, `pulsar-blink` |

Frames live in `macos/Pulsar/Sources/Resources/`. Pre-Rev-8 masters are retained at `design/drones/pre-rev8/` and the original
pre-machined cast at `design/drones/before/`. Meridian's Rev 9 master was
generated as four FULL re-renders rather than masked edits, after compounding
inpaints produced a chest emblem and glow that read as applied rather than
rendered.

## Prompts

The full prompt text for each generation is preserved in the build scratchpad
alongside each attempt (`prompt-<drone>-<attempt>.txt`). The governing standard,
including every ruling that shaped these designs, is `design/FACTORY-STYLE.md`
(revisions 1-8, with the rationale for each change recorded in the git history).

## Characters are fictional

The nine drones are invented cognitive frames — names, voices and faces given to
sub-agents so a user can tell concurrent work apart by ear and on screen. None is
a real person, an employee, or a portrait of anyone.
