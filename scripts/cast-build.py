#!/usr/bin/env python3
"""Build the cast until it passes the gate.

Generates, registers, stamps provenance, gates — then re-renders only the failures
with a correction aimed at the specific check that failed, and repeats. Prompts have
never held framing, hue, glow or pose on their own, so the gate is the arbiter and
this is the loop that feeds it.

  python3 scripts/cast-build.py [--rounds N] [--only drone ...]
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
CAST = ["pulsar", "voyager", "sentinel", "nova", "nebula",
        "echo", "atlas", "iris", "meridian", "vector"]

# THE STANDARD — signed off by Justin on 2026-08-13. These seven are what the rest of
# the cast is measured against.
#
# They are NOT frozen: ask for one by name (--only nebula) and it re-renders, which is
# how a deliberate tweak gets made. What they are protected from is being re-rolled
# INCIDENTALLY — the generator takes no seed, so an automatic re-render rolls a brand
# new face and throws away the thing that was approved. A comparative check flagging a
# standard-bearer because a sibling drifted is a fact about the SIBLING; the sibling
# moves back, not the standard.
STANDARD = {"pulsar", "voyager", "nova", "nebula", "atlas", "iris", "meridian"}

# What to say to the model when a given check fails. Keyed by a fragment of the
# gate's failure text.
# NOTE: the "chest orb" correction was REMOVED. Justin repealed the orb ban
# ("the glowing orb parts can exist but they do not need to influence the crop"),
# and the gate stopped failing on orbs — but the correction kept injecting an
# anti-orb paragraph, which brief_drift then correctly flagged as a brief still
# enforcing a repealed rule. A correction outliving its check is a defect.
CORRECTIONS = {
    "turned": (
        "CRITICAL POSE FAILURE — THE LAST RENDER OF THIS CHARACTER WAS TURNED AWAY FROM "
        "CAMERA and was rejected by an automated head-pose check. The head must be PERFECTLY "
        "SQUARE TO CAMERA: zero yaw, zero rotation, both cheeks showing equally, both ears "
        "equally visible, the nose and mouth exactly on the vertical centreline, gaze straight "
        "down the lens. Think passport photograph. This overrides every compositional instinct."),
    "tilted": (
        "POSE FAILURE — the last render had the head TILTED. The line between the two eyes must "
        "be exactly horizontal, with no roll and no jaunty angle."),
    "chin": (
        "POSE FAILURE — the last render had the chin raised or dropped. The camera is at eye "
        "level and the head is level: no chin lift, no chin tuck, no looking up or down."),
    "eyes dim": (
        "EYE BRIGHTNESS FAILURE — the last render had irises that were too dark and was "
        "rejected by an automated brightness check. BOTH IRISES MUST BLAZE: a hot, saturated, "
        "self-luminous ring in the character's colour, near-white at its hottest, casting a "
        "visible coloured glow onto the lower eyelid and the inner corner of the eye socket. "
        "They are the brightest element on the entire face. A dim tinted eye, a dark coloured "
        "lens or a subtle shimmer all fail. The pupil remains a dark hole at the centre."),
    "glow": (
        "GLOW FAILURE — the last render was too bright and was rejected. Cut the emissive area "
        "back hard: keep the lit lining fine and thin, keep facial grooves narrow, and let the "
        "irises be the brightest thing. No broad blooms, no wide washes of colour, no glowing "
        "areas larger than a fingertip apart from the eyes."),
    "eyeCy": (
        "FRAMING FAILURE — head and shoulders, with the crown a short margin below the top edge "
        "and the eye line a little above the middle of the frame. Do not shoot from far back and "
        "do not crop the top of the head."),
    "IOD": (
        "FRAMING FAILURE — the head was the wrong size in frame. Head and shoulders, filling the "
        "frame comfortably, with the distance between the pupils about a fifth of the image width."),
    "background has scenery": (
        "BACKGROUND FAILURE — there was structure or texture behind the subject. The background "
        "is a FLAT, EMPTY, NEAR-BLACK void with only the faintest haze of the character's colour. "
        "No set, no wall, no panelling, no machinery, no gradient banding, no visible surface."),
    "headroom": (
        "HEADROOM FAILURE — the top of the head ran off the top edge of the frame and was "
        "rejected. The shot is NOT going to be widened: the whole cast shares one fixed zoom "
        "and one fixed eye line. Fix it by giving the character a LOWER SILHOUETTE ABOVE THE "
        "EYES — hair worn closer to the skull, any hood or headgear low-profile and following "
        "the shape of the head, nothing stacked or piled on the crown. There must be clear "
        "empty space between the top of the head and the top of the picture."),
    "head is CUT OFF": (
        "HEADROOM FAILURE — the top of the head ran off the top edge of the frame and was "
        "rejected. The shot is NOT going to be widened: the whole cast shares one fixed zoom "
        "and one fixed eye line. Fix it by giving the character a LOWER SILHOUETTE ABOVE THE "
        "EYES — hair worn closer to the skull, any hood or headgear low-profile and following "
        "the shape of the head, nothing stacked or piled on the crown. There must be clear "
        "empty space between the top of the head and the top of the picture."),
    "head": (
        "HEAD SIZE FAILURE — the head was rendered at the wrong scale relative to the rest of "
        "the cast, and was rejected. Every portrait must sit at the SAME distance from camera: "
        "the head from crown to chin occupies a little over a third of the frame height. Not a "
        "distant bust, not a tight beauty crop. Match the style anchor's head size exactly — "
        "hold a ruler to it. This is a cast of colleagues photographed in one sitting, on one "
        "lens, at one distance."),
    "key light": (
        "LIGHTING FAILURE — the key light was on the wrong side, or the face was lit flat and "
        "shadowless, and was rejected. The KEY LIGHT COMES FROM THE CHARACTER'S LEFT (the "
        "viewer's right), roughly forty-five degrees off axis and slightly above eye level. The "
        "far cheek falls into soft shadow about a stop down — visible modelling on the nose, the "
        "brow and the jaw. Flat frontal lighting reads as a snapshot and breaks the set."),
    "converges with": (
        "SILHOUETTE COLLISION — at menu-bar size this character is indistinguishable from a "
        "sibling, and was rejected. It must be recognisable as a THUMBNAIL, where all that "
        "survives is the outline, the hair mass, the headgear shape and the colour. Push the "
        "read-at-a-glance features hard apart from the rest of the cast: a distinctly different "
        "hair volume and outline, a different headgear profile, a different shoulder line. "
        "Detail that only appears at full resolution does not count."),
    "face converges": (
        "FACE COLLISION — the underlying facial geometry is too close to another character's and "
        "was rejected by a landmark-distance check. Rebuild the face from different bones: change "
        "the face SHAPE (long vs square vs heart vs round), the eye spacing and set, the nose "
        "length and bridge width, the mouth width, the jaw angle and the brow height. Two people "
        "with different hair and the same skull are the same person in a wig."),
    "warm-metal": (
        "MATERIAL FAILURE — the body carried no warm metal and was rejected. Brass, bronze or "
        "aged copper is the cast's shared material signature: it must appear on the manufactured "
        "parts of the NECK, SHOULDERS AND COLLAR — plate edges, seam bolts, a jack housing, "
        "shoulder hardware — as a visible, unmistakable warm metal against the charcoal uniform. "
        "Not a faint tint, not a highlight; actual metal you could name."),
    "hue_fid": (
        "COLOUR FAILURE — the rendered accent drifted off this character's locked colour and was "
        "rejected. The lit elements — iris rings, the fine collar and yoke piping, the facial "
        "grooves, the indicator lamp and the background spill — must ALL be the exact locked hex "
        "stated below. Do not shift it toward a neighbouring hue, do not stylise it, do not let "
        "the light temperature pull it. One colour, one character."),
}


# ---------------------------------------------------------------------------
# THE RATCHET.
#
# The loop used to re-render every failing character each round and keep
# whatever came back. Because the generator takes no seed, "re-render" means a
# brand-new face — so a drone that failed one check out of fourteen threw away
# thirteen passes and rolled again. Across eighteen gate runs the cast never got
# past 1/10, not because the images were bad but because progress was being
# discarded every round.
#
# Now: every render is scored by how many checks it fails, the best-ever render
# per character is archived, and a new render is only promoted if it is STRICTLY
# better. A worse roll is thrown away and the incumbent restored. Progress can
# no longer go backwards, which is what makes the loop terminate.
# ---------------------------------------------------------------------------
BESTDIR = os.path.join(ROOT, "generated-images", "best")
BESTMETA = os.path.join(BESTDIR, "provenance.json")
BEST = {}


def _load_meta():
    """Which brief produced each archived best — persisted, not recomputed.

    Recomputing the hash at startup compares the current brief with itself, so it
    always matches and the reset never fires. That is precisely how two rewritten
    characters were silently rolled back twice: their briefs had been rewritten to
    order, the renders implemented the rewrite, and the ratchet discarded them for
    scoring no better against a baseline set by the OLD spec.
    """
    try:
        with open(BESTMETA) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save_meta(meta):
    os.makedirs(BESTDIR, exist_ok=True)
    with open(BESTMETA, "w") as f:
        json.dump(meta, f, indent=2, sort_keys=True)


def _files(d):
    g = os.path.join(ROOT, "generated-images")
    return [os.path.join(g, f"{d}-android-v8.png"),
            os.path.join(g, f"{d}-android-v8-aligned.png")]


def keep(d):
    os.makedirs(BESTDIR, exist_ok=True)
    for f in _files(d):
        if os.path.exists(f):
            shutil.copy2(f, os.path.join(BESTDIR, os.path.basename(f)))


def restore(d):
    for f in _files(d):
        b = os.path.join(BESTDIR, os.path.basename(f))
        if os.path.exists(b):
            shutil.copy2(b, f)


def brief_hash(d):
    """SHA of this character's WHOLE spec — the locked colour AND the brief text.

    The colour was originally left out of the hash, and that silently defeated the
    whole mechanism: the cast was moved onto a new palette, every hex changed, and
    the hash did not move — so the ratchet saw "same spec, no better score" and
    rolled eight characters back to their OLD COLOURS. The bug reads as nothing
    happening, which is the worst kind. The locked hex IS part of the specification.
    """
    src = open(os.path.join(SCRIPTS, "cast-generate.py")).read()
    m = re.search(r'\(\s*"%s",\s*"(#[0-9A-Fa-f]{6})",\s*"""(.*?)"""' % d, src, re.S)
    if not m:
        return None
    return hashlib.sha256((m.group(1) + m.group(2)).encode()).hexdigest()[:16]


BRIEF_AT_BEST = {}


def ratchet(targets, fails):
    """Promote only improvements; roll back everything else. Returns names kept."""
    kept, rolled = [], False
    for d in targets:
        score = len(fails.get(d, []))
        prior = BEST.get(d)
        # If the BRIEF changed since this character's best was archived, the old score
        # is not a baseline any more — it belongs to a different specification. The
        # ratchet optimises gate score, and gate score is blind to design intent: it
        # threw away rewritten Sentinel, Echo and Vector renders that carried exactly
        # the fixes that had been asked for, purely because they scored no better.
        # A deliberate spec change resets the bar.
        h = brief_hash(d)
        if prior is not None and BRIEF_AT_BEST.get(d) != h:
            print(f"    {d}: brief changed — accepting the new render as the baseline")
            prior = None
        if prior is None or score < prior:
            BRIEF_AT_BEST[d] = h
            _meta = _load_meta()
            _meta[d] = h
            _save_meta(_meta)
            BEST[d] = score
            keep(d)
            kept.append(f"{d} {prior if prior is not None else '-'}->{score}")
        else:
            restore(d)
            rolled = True
    if rolled:
        # Re-archive. A rolled-back render leaves masters-archive/ pointing at the
        # roll we just DISCARDED, so `lineage` then fails the restored drone for
        # not matching a master it never came from. That is a defect in this
        # ratchet, not in the picture — and it showed up as ten spurious drift
        # failures against a cast that had gated clean moments earlier.
        run([sys.executable, os.path.join(SCRIPTS, "cast-provenance.py")])
    return kept



def run(cmd, **kw):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                          text=True, cwd=ROOT, **kw)


def gate():
    """Run the gate; return {drone: [failure strings]} for failures only."""
    r = run([sys.executable, os.path.join(SCRIPTS, "cast-gate.py"), "v8"])
    out = r.stdout
    fails = {}
    for line in out.splitlines():
        m = re.match(r"^(\w+)\s+.*?FAIL:\s*(.+)$", line.strip())
        if m and m.group(1) in CAST:
            fails[m.group(1)] = [x.strip() for x in m.group(2).split(",")]
    return fails, out


ACCUMULATED = {}


def inject(drone, notes):
    """Add corrections to a character's brief, KEEPING every earlier one.

    Replacing the block each round made defects oscillate: a character that stopped
    failing the orb check lost its orb instruction and grew the orb straight back on
    the following round. A correction, once earned, stays.
    """
    prior = ACCUMULATED.setdefault(drone, [])
    for nt in notes:
        if nt not in prior:
            prior.append(nt)
    notes = prior
    p = os.path.join(SCRIPTS, "cast-generate.py")
    s = open(p).read()
    i = s.index(f'    ("{drone}", "')
    nxt = CAST[CAST.index(drone) + 1] if CAST.index(drone) + 1 < len(CAST) else None
    j = s.index(f'    ("{nxt}", "') if nxt else s.index("\n]\n")
    blk = s[i:j]
    blk = re.sub(r"\n\n=== AUTOMATED CORRECTION ===.*?=== END CORRECTION ===\n", "\n", blk, flags=re.S)
    k = blk.rindex('"""),')
    body = "\n\n=== AUTOMATED CORRECTION ===\n" + "\n\n".join(notes) + "\n=== END CORRECTION ===\n"
    s = s[:i] + blk[:k] + body + blk[k:] + s[j:]
    open(p, "w").write(s)


def _api_key():
    """GEMINI_API_KEY lives in ~/.zshrc, which only an INTERACTIVE zsh sources.
    Fetch it once and pass it through the environment; shelling out through
    `zsh -ic` per call silently produced 'API key not valid' on every generation."""
    k = os.environ.get("GEMINI_API_KEY")
    if k:
        return k
    r = subprocess.run(["zsh", "-ic", "printf %s \"$GEMINI_API_KEY\""],
                       capture_output=True, text=True)
    k = (r.stdout or "").strip()
    # ~/.zshrc can carry several exports and the LAST one wins — including a
    # leftover "<your-key>" placeholder, which silently shadows the real key and
    # turns every generation into a 400. Fall back to the last real-looking value.
    if not k or k.startswith("<") or len(k) < 20:
        rc = os.path.expanduser("~/.zshrc")
        cands = []
        if os.path.exists(rc):
            for line in open(rc):
                m = re.search(r'GEMINI_API_KEY\s*=\s*"?([^"\s]+)"?', line)
                if m:
                    v = m.group(1)
                    if not v.startswith("<") and len(v) >= 20:
                        cands.append(v)
        if cands:
            print(f"    note: shell resolved a placeholder key; using the real one "
                  f"from ~/.zshrc ({len(cands[-1])} chars)")
            k = cands[-1]
    if not k or k.startswith("<") or len(k) < 20:
        sys.exit("No usable GEMINI_API_KEY — ~/.zshrc has a '<your-key>' placeholder "
                 "shadowing the real value. Delete the placeholder lines.")
    os.environ["GEMINI_API_KEY"] = k
    return k


def generate(drones):
    env = dict(os.environ)
    env["GEMINI_API_KEY"] = _api_key()
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "cast-generate.py"), *drones],
                       capture_output=True, text=True, cwd=ROOT, env=env)
    ok = [l.strip().split(":")[0] for l in r.stdout.splitlines() if ": OK" in l]
    for l in r.stdout.splitlines():
        if ": OK" not in l and l.strip() and "generated" not in l:
            print("    " + l.strip()[:110])
    return ok


def pipeline():
    run([sys.executable, os.path.join(SCRIPTS, "cast-align.py"), "v8"])
    run([sys.executable, os.path.join(SCRIPTS, "cast-provenance.py")])


ap = argparse.ArgumentParser()
ap.add_argument("--rounds", type=int, default=4)
ap.add_argument("--only", nargs="*", default=None)
a = ap.parse_args()

# Spec parity first: every drone held to the same standard before a pixel is made.
lint = run([sys.executable, os.path.join(SCRIPTS, "cast-lint.py")])
if lint.returncode != 0:
    print(lint.stdout)
    sys.exit("spec lint failed — fix the briefs before generating")
print("spec lint: PASS\n")

targets = a.only or CAST

# Seed the ratchet from whatever is already on disk. Without this, every rerun
# throws away the standing cast and re-baselines from a fresh roll — the same
# discard-your-progress bug the ratchet exists to kill, just at run granularity
# instead of round granularity.
_seed_fails, _ = gate()
_seed_meta = _load_meta()
for _d in CAST:
    BEST[_d] = len(_seed_fails.get(_d, []))
    BRIEF_AT_BEST[_d] = _seed_meta.get(_d)
    keep(_d)
_clean = sum(1 for v in BEST.values() if v == 0)
print(f"seeded from the cast on disk: {_clean}/{len(CAST)} already clean "
      f"({', '.join(f'{k} {v}' for k, v in sorted(BEST.items(), key=lambda kv: -kv[1]) if v)})\n")

print(f"building {len(targets)} characters, up to {a.rounds} rounds\n")

for rnd in range(1, a.rounds + 1):
    print(f"─── round {rnd} ─── generating: {', '.join(targets)}")
    # pulsar first when present: he is the style anchor the others reference
    if "pulsar" in targets:
        generate(["pulsar"])
        rest = [d for d in targets if d != "pulsar"]
    else:
        rest = list(targets)
    if rest:
        generate(rest)
    pipeline()
    fails, table = gate()
    moved = ratchet(targets, fails)
    if moved:
        print(f"    kept: {', '.join(moved)}")
    worse = [d for d in targets if d not in " ".join(moved)]
    if worse:
        # Rolled back, so the table above no longer describes what is on disk.
        fails, table = gate()
    passed = len(CAST) - len(fails)
    print(f"    gate: {passed}/{len(CAST)} pass   (best-so-far "
          f"{sum(1 for v in BEST.values() if v == 0)}/{len(CAST)} clean)")
    for d, fs in fails.items():
        print(f"      {d:10} {'; '.join(fs)}")
    if not fails:
        print("\nall ten pass the gate")
        break
    # A character asked for by name stays in play even if it is a standard-bearer:
    # that is a deliberate tweak. Everything else is protected from incidental re-rolls.
    requested = set(a.only or [])
    targets = [d for d in fails if d not in STANDARD or d in requested]
    held = [d for d in fails if d not in targets]
    if held:
        print(f"    holding the standard: {', '.join(held)} "
              f"(flagged, not re-rolled — name them with --only to tweak)")
    if not targets:
        print("\nremaining failures are all on standard-bearers nobody asked to change — "
              "stopping rather than re-rolling an approved face")
        break
    for d, fs in fails.items():
        notes = []
        for f in fs:
            for key, text in CORRECTIONS.items():
                if key in f and text not in notes:
                    notes.append(text)
            # Name the sibling it collided with. "Differ from another character"
            # is not an instruction a renderer can follow; "differ from Meridian,
            # who has X" is. The gate already knows who — pass it through.
            m = re.search(r"converges (?:with|on) (\w+)", f)
            if m and m.group(1) in CAST:
                other = m.group(1)
                nt = (f"The character it collided with is {other.upper()}. Study {other}'s "
                      f"portrait and move DECISIVELY away from it — different face shape, "
                      f"different hair mass and outline, different headgear profile. "
                      f"{d.upper()} and {other.upper()} must be tellable apart by outline alone.")
                if nt not in notes:
                    notes.append(nt)
        if notes:
            inject(d, notes)
    print()

print()
print(gate()[1])
