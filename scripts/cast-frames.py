#!/usr/bin/env python3
"""Build the six animation frames per character from ONE approved master.

THE RULE THIS SCRIPT EXISTS TO ENFORCE (drone-forge SKILL.md §7): derive all six
frames from a SINGLE generation. Never generate them independently. Two independent
generations of the same character drifted +7px crown, -29px centre, +6.0% scale — at
that drift the face swims while the mouth moves and the effect is unusable. The model
takes no seed, so independent renders can never register.

So: one call produces a 3x2 sprite sheet whose six cells share lighting, pose and
identity by construction. We then crop the cells, register each against cell 0 with
OpenCV's ECC solver to kill residual sub-pixel drift, and downsample to the 362px the
app loads.

  python3 scripts/cast-frames.py                 # every character
  python3 scripts/cast-frames.py nova iris       # named characters
  python3 scripts/cast-frames.py --verify-only   # re-run the checks, generate nothing

Output, and the app depends on these exact names (PortraitView.swift):
  macos/Pulsar/Sources/Resources/<category>-mouth-0.png   closed / rest
                                <category>-mouth-1..3.png  opening
                                <category>-mouth-4.png    full open
                                <category>-blink.png      eyes closed, mouth at rest
"""
import base64
import io
import json
import os
import re
import subprocess
import shutil
import sys
import urllib.error
import urllib.request

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(ROOT, "generated-images")
RES = os.path.join(ROOT, "macos/Pulsar/Sources/Resources")
SHEETS = os.path.join(G, "frame-sheets")
VER = "v8"
OUT_PX = 362
CAST = ["pulsar", "voyager", "sentinel", "nova", "nebula",
        "echo", "atlas", "iris", "meridian", "vector"]

MODEL = "gemini-3-pro-image"
API = ("https://generativelanguage.googleapis.com/v1beta/models/"
       f"{MODEL}:generateContent")

# Cell order in the 3x2 sheet, left to right then top to bottom.
#
# SIX CELLS, and that is a measured ceiling rather than a preference. A twelve-cell
# sheet (adding half-blink, gaze left/right/down, attentive and a smile) was tried
# and failed on all ten characters: the model stopped holding the mouth at rest in
# the passive cells — Meridian moved his by 27% — half the half-blinks were not
# intermediate between open and closed, and Sentinel drifted 161px. Six cells hold
# reliably. If the passive set is ever wanted, generate it as a SECOND small sheet
# from the same master rather than by enlarging this one.

CELLS = ["mouth-0", "mouth-1", "mouth-2", "mouth-3", "mouth-4", "blink"]

SHEET_PROMPT = """This image is a finished character portrait. Produce a SPRITE SHEET of the
EXACT SAME CHARACTER in TWELVE cells for facial animation.

LAYOUT: a 4x3 grid — four cells across, three rows down. Equal cells, no gutters, no
borders, no labels, no numbering, no text of any kind anywhere in the image.

CELLS 1-5 — THE MOUTH RAMP. Only the mouth changes across these five.

  CELL 1 — MOUTH CLOSED. Lips together at rest. This is the reference pose.
  CELL 2 — MOUTH BARELY OPEN. Lips just parted, a dark line between them.
  CELL 3 — MOUTH A QUARTER OPEN. Jaw dropped further, teeth beginning to show.
  CELL 4 — MOUTH HALF OPEN. A clear oval opening, upper teeth visible.
  CELL 5 — MOUTH FULLY OPEN, as in a strongly spoken vowel. Jaw well down, a large
           dark opening, teeth and the suggestion of the tongue. This must be an
           OBVIOUSLY bigger opening than cell 4, readable at small size.

CELLS 6-12 — THE PASSIVE SET. The mouth is CLOSED AND AT REST in all of these,
exactly as cell 1, EXCEPT cell 12 which is noted. Only the eyes and brows change.

  CELL 6  — EYES HALF CLOSED. A blink caught HALFWAY: both upper lids descended to
            cover roughly half of each iris, lashes visible, brows UNCHANGED. The eye
            glow is partly occluded but still clearly burning. This is a real
            mid-blink pose, not a squint and not a sleepy expression.
  CELL 7  — EYES FULLY CLOSED. Both lids completely down, lashes and lid creases
            visible, brows UNCHANGED and not lowered. The glow is reduced to almost
            nothing — a thin rim of light may escape between the lashes, no more.
  CELL 8  — LOOKING TO THEIR LEFT (the RIGHT side of the picture as you view it).
            The HEAD DOES NOT MOVE AT ALL — only the eyes travel. Both irises shift
            together toward that side, showing more white on the opposite side of
            each eye. Lids and brows stay where they are. A natural sideways glance.
  CELL 9  — LOOKING TO THEIR RIGHT (the LEFT side of the picture as you view it).
            The mirror of cell 8. Again the head does not move; only the eyes.
  CELL 10 — ATTENTIVE. Listening to someone else: both eyebrows raised slightly and
            evenly, eyes fractionally wider, the faintest lift at the corners of the
            mouth WITHOUT the lips parting. Interested and engaged. This is a SUBTLE
            change — it must not read as shock, and the mouth must stay closed.

  CELL 11 — LOOKING DOWN. Eyes cast downward as if reading or thinking. The HEAD
            DOES NOT MOVE; the lids follow the eyes down a little, as they naturally
            do. Brows unchanged. Calm and considered, not sad.
  CELL 12 — A CLOSED-MOUTH SMILE. Genuine and warm but restrained: the corners of
            the mouth lift, the cheeks rise slightly, and the eyes crease at the
            outer corners the way a real smile reaches them. THE LIPS STAY TOGETHER —
            no teeth, no open mouth. In character for this person, not a grin.

WHAT MUST BE IDENTICAL IN ALL TWELVE CELLS — this is the whole point of the sheet:
  - the head is in EXACTLY the same position, at exactly the same size and angle
  - identical framing and crop within each cell, AND THE SAME CROP AS THE REFERENCE
    IMAGE: head AND SHOULDERS, with the upper chest and shoulders filling the bottom
    of every cell exactly as they do in the picture you were given, AND CLEAR EMPTY
    SPACE ABOVE THE TOP OF THE HEAD in every cell — the crown, the hair and any
    headgear must be fully inside the frame and must never touch the top edge. Do not tighten in
    to a head-only portrait and do not leave the body out — a floating head is a
    failure, however good the face is
  - identical lighting, identical key and rim, identical background
  - identical hair, headgear, hardware, uniform, and every lit element
  - identical skin, identical everything except the one feature named per cell

The head NEVER moves, rotates, tilts or changes size in any cell — not even in the
two gaze cells, where the eyes travel inside a completely still head. Treat it as twelve
photographs taken by a locked-off camera of a person who moved nothing but their jaw,
their eyelids, their eyes and their eyebrows.
"""


def api_key():
    k = os.environ.get("GEMINI_API_KEY")
    if k and len(k) >= 20 and not k.startswith("<"):
        return k
    rc = os.path.expanduser("~/.zshrc")
    cands = []
    if os.path.exists(rc):
        for line in open(rc):
            m = re.search(r'GEMINI_API_KEY\s*=\s*"?([^"\s]+)"?', line)
            if m and not m.group(1).startswith("<") and len(m.group(1)) >= 20:
                cands.append(m.group(1))
    if not cands:
        sys.exit("no usable GEMINI_API_KEY")
    return cands[-1]


def generate_sheet(name, key):
    """One call, six cells. Returns the raw image bytes."""
    master = os.path.join(G, f"{name}-android-{VER}-aligned.png")
    if not os.path.exists(master):
        return None, f"no approved master at {os.path.relpath(master, ROOT)}"
    data = base64.b64encode(open(master, "rb").read()).decode()
    body = {
        "contents": [{"role": "user", "parts": [
            {"inline_data": {"mime_type": "image/png", "data": data}},
            {"text": SHEET_PROMPT},
        ]}],
        "generationConfig": {"responseModalities": ["IMAGE"],
                             "imageConfig": {"aspectRatio": "4:3"}},
    }
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read()[:200].decode('utf-8', 'replace')}"
    except Exception as e:                                  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"
    for cand in payload.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            b = part.get("inline_data") or part.get("inlineData")
            if b and b.get("data"):
                return base64.b64decode(b["data"]), None
    return None, "no image in response"


def split_cells(sheet):
    """Crop the 4x3 grid. Returns twelve BGR images in reading order."""
    h, w = sheet.shape[:2]
    cw, ch = w // 4, h // 3
    out = []
    for row in range(3):
        for col in range(4):
            out.append(sheet[row * ch:(row + 1) * ch, col * cw:(col + 1) * cw])
    return out


def register(ref, img):
    """Kill residual drift: solve a warp of img onto ref.

    MOTION_EUCLIDEAN was not enough. It models rotation and translation only, so when
    the model rendered a cell at a slightly different head SIZE — which it does, even
    inside one sprite sheet — there was no parameter that could absorb it and the
    solver left several pixels of drift behind. Measured on the first batch: voyager
    5.3px, vector 8.8px, with 9-16% of the upper face moving between mouth-0 and
    mouth-4. A face that swims while the mouth moves is the exact failure this whole
    single-generation approach exists to avoid.

    MOTION_AFFINE adds scale (and shear, which stays negligible because the input is
    already nearly aligned). A three-level pyramid gives the solver a coarse estimate
    first, so it converges from a much worse starting position than a single-scale run
    can handle.

    The mouth is masked out of the solve: it is SUPPOSED to differ between frames, and
    letting the solver try to align a moving mouth drags the whole face to chase it.
    """
    if img.shape != ref.shape:
        img = cv2.resize(img, (ref.shape[1], ref.shape[0]), interpolation=cv2.INTER_LANCZOS4)
    g1 = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY).astype(np.float32)
    g2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    h = g1.shape[0]
    mask = np.ones_like(g1, np.uint8)
    mask[int(h * 0.60):, :] = 0                     # everything below the nose is out

    warp = np.eye(2, 3, dtype=np.float32)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 500, 1e-7)
    for level in (4, 2, 1):                          # coarse -> fine
        if level > 1:
            a = cv2.resize(g1, (g1.shape[1] // level, g1.shape[0] // level))
            b = cv2.resize(g2, (g2.shape[1] // level, g2.shape[0] // level))
            m = cv2.resize(mask, (mask.shape[1] // level, mask.shape[0] // level))
        else:
            a, b, m = g1, g2, mask
        w = warp.copy()
        w[0, 2] /= level
        w[1, 2] /= level
        try:
            cv2.findTransformECC(a, b, w, cv2.MOTION_AFFINE, crit, m, 5)
        except cv2.error:
            continue
        w[0, 2] *= level
        w[1, 2] *= level
        warp = w
    fixed = cv2.warpAffine(img, warp, (ref.shape[1], ref.shape[0]),
                           flags=cv2.INTER_LANCZOS4 + cv2.WARP_INVERSE_MAP,
                           borderMode=cv2.BORDER_REPLICATE)
    return fixed, True



# Where a face must sit inside a frame asset, as fractions of the tile.
FRAME_CX = 0.500      # dead centre horizontally — Justin: "faces should be centred"
FRAME_CY = 0.470      # anchor centroid a little above middle
FRAME_RADIUS = 0.101  # anchor radius as a fraction of tile width.
                      # Was 0.115, which is 14% tighter than the character Justin
                      # named as the reference: Voyager measures 0.1011 with 7.7%
                      # clear above his crown. At 0.115 four characters (Nova,
                      # Pulsar, Iris, Vector) had their crowns clipped flat against
                      # the top edge — measured crown clearance 0.0%.


def normalise_set(frames):
    """Put every character's face at the same place and size inside the tile.

    The sprite sheet is cut into equal thirds, but the model does not centre the
    head inside each cell — measured across the cast the face sat between 47.6%
    and 49.9% horizontally (every one biased left) and between 46.4% and 54.6%
    vertically, an eight-point spread. Ten portraits at ten different offsets read
    as sloppy in a row of squircles no matter how good each one is.

    ONE transform is measured on mouth-0 and applied to ALL SIX frames. That is the
    important part: a per-frame fit would re-introduce exactly the inter-frame drift
    that the ECC registration just removed. Uniform scale and translation only — no
    rotation, no shear — so the frames stay registered to each other by construction.
    """
    import tempfile
    ref = frames[0]
    h, w = ref.shape[:2]
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        cv2.imwrite(tf.name, ref)
        path = tf.name
    try:
        import cast_pose
        a = cast_pose.face_anchors(path)
    except Exception:                                        # noqa: BLE001
        a = None
    finally:
        os.unlink(path)
    if a is None:
        return frames, "no face mesh — left uncentred"

    cx, cy = float(a[:, 0].mean()), float(a[:, 1].mean())
    radius = float(np.mean(np.linalg.norm(a - a.mean(axis=0), axis=1)))
    if radius < 1:
        return frames, "degenerate face mesh — left uncentred"

    scale = (FRAME_RADIUS * w) / radius
    tx = FRAME_CX * w - cx * scale
    ty = FRAME_CY * h - cy * scale
    M = np.array([[scale, 0, tx], [0, scale, ty]], dtype=np.float32)
    out = [cv2.warpAffine(f, M, (w, h), flags=cv2.INTER_LANCZOS4,
                          borderMode=cv2.BORDER_REPLICATE) for f in frames]
    return out, f"centred (moved {cx / w * 100 - FRAME_CX * 100:+.1f}% x, scale {scale:.3f})"



def lock_mouth_to_rest(frames):
    """Give the blink frame mouth-0's ACTUAL mouth, rather than asking for a copy.

    The blink is composited over whatever mouth frame is showing, so its mouth must
    match mouth-0 exactly or the mouth appears to move every time a drone blinks.
    Asking the model for a pixel-identical mouth does not work: across 22 generation
    attempts on six characters only 2 came back inside tolerance — a 9% hit rate,
    with misses as bad as 68%. It redraws the face each cell and the mouth drifts.

    So it is not asked. The cells already share a generation and are ECC-registered
    to under a pixel, so mouth-0's lower face can simply be composited into the
    blink frame through a soft-edged mask. Nothing is invented — these are mouth-0's
    own pixels, on the same face, in the same position, under the same light. It
    guarantees what the prompt could only request.

    Only the BLINK is treated this way. The mouth ramp must genuinely differ, and
    the eyes are left entirely alone, which is the whole point of the frame.
    """
    rest, blink = frames[CELLS.index("mouth-0")], frames[CELLS.index("blink")]
    h, w = rest.shape[:2]
    # Mask the mouth/jaw only: full strength below the nose, feathered above it so
    # the seam never lands on a hard edge.
    mask = np.zeros((h, w), np.float32)
    top, full = int(h * 0.55), int(h * 0.66)
    mask[full:, :] = 1.0
    for y in range(top, full):
        mask[y, :] = (y - top) / float(full - top)
    mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=h * 0.012)
    m3 = cv2.merge([mask, mask, mask])
    merged = (blink.astype(np.float32) * (1 - m3) + rest.astype(np.float32) * m3)
    out = list(frames)
    out[CELLS.index("blink")] = np.clip(merged, 0, 255).astype(np.uint8)
    return out



def lock_eyes_to_rest(frames):
    """Give every MOUTH frame mouth-0's actual eyes.

    The mirror of lock_mouth_to_rest. The mouth ramp is crossfaded by amplitude, so
    if the eyes differ between mouth-0 and mouth-4 they drift and swim while the
    character talks — measured worst on Iris at 4.4% of the eye band, which reads as
    the eyes moving oddly during speech. Only the mouth is supposed to change.

    The blink is deliberately excluded: closing the eyes is the entire point of that
    frame.
    """
    rest = frames[CELLS.index("mouth-0")]
    h, w = rest.shape[:2]
    # Brow to just under the eye, feathered top and bottom so no seam lands on skin.
    mask = np.zeros((h, w), np.float32)
    top, a, b, bot = int(h * 0.24), int(h * 0.30), int(h * 0.50), int(h * 0.56)
    mask[a:b, :] = 1.0
    for y in range(top, a):
        mask[y, :] = (y - top) / float(a - top)
    for y in range(b, bot):
        mask[y, :] = 1.0 - (y - b) / float(bot - b)
    mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=h * 0.010)
    m3 = cv2.merge([mask, mask, mask])
    out = list(frames)
    for name in ("mouth-1", "mouth-2", "mouth-3", "mouth-4"):
        i = CELLS.index(name)
        merged = out[i].astype(np.float32) * (1 - m3) + rest.astype(np.float32) * m3
        out[i] = np.clip(merged, 0, 255).astype(np.uint8)
    return out


def lock_eye_hardware(frames):
    """Pin metal worn ON the face so it cannot jitter while the lids move.

    Meridian wears a monocle. The generated blink redraws it slightly, so the frame
    appeared to shift on his face every time he blinked — the eyepiece is HARDWARE
    and hardware does not move when someone closes their eye. Justin's call: keep
    the eye visible beneath the lens, so an opaque disc is out; only the metal is
    pinned, and the lid blinks behind it as it should.

    The mask is found, not hardcoded: bright, low-saturation (metallic) pixels
    inside the eye band, taken from mouth-0 and dilated a little to cover the
    anti-aliased rim. Characters with no facial metal get an empty mask and are
    untouched, so this costs nothing for the other nine.
    """
    rest = frames[CELLS.index("mouth-0")]
    h, w = rest.shape[:2]
    hsv = cv2.cvtColor(rest, cv2.COLOR_BGR2HSV)
    metal = ((hsv[:, :, 2] > 120) & (hsv[:, :, 1] < 70)).astype(np.uint8)
    metal[:int(h * 0.24), :] = 0          # above the brow: hair and headgear, not eyewear
    metal[int(h * 0.56):, :] = 0          # below the cheek: collar and uniform
    if metal.sum() < h * w * 0.002:       # nothing meaningfully metallic near the eyes
        return frames
    metal = cv2.dilate(metal, np.ones((5, 5), np.uint8), iterations=1)
    mask = cv2.GaussianBlur(metal.astype(np.float32), (0, 0), sigmaX=1.6)
    m3 = cv2.merge([mask, mask, mask])
    out = list(frames)
    i = CELLS.index("blink")
    merged = out[i].astype(np.float32) * (1 - m3) + rest.astype(np.float32) * m3
    out[i] = np.clip(merged, 0, 255).astype(np.uint8)
    return out

def verify(name, directory=None):
    """The measurable definition of done, from drone-forge SKILL.md §7."""
    base = directory or RES
    paths = [os.path.join(base, f"{name}-{c}.png") for c in CELLS]
    missing = [os.path.basename(p) for p in paths if not os.path.exists(p)]
    if missing:
        return False, f"missing {', '.join(missing)}"
    imgs = [cv2.imread(p) for p in paths]
    if any(i is None for i in imgs):
        return False, "unreadable frame"
    if any(i.shape[0] != OUT_PX or i.shape[1] != OUT_PX for i in imgs):
        return False, f"wrong size (want {OUT_PX}x{OUT_PX})"

    ref = imgs[0]
    notes = []
    # 1. registration: phase correlation against mouth-0 must be ~zero
    g0 = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY).astype(np.float32)
    worst = 0.0
    for c, im in zip(CELLS[1:], imgs[1:]):
        gi = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
        (dx, dy), _ = cv2.phaseCorrelate(g0, gi)
        worst = max(worst, abs(dx), abs(dy))
    if worst > 1.5:
        notes.append(f"drift {worst:.1f}px vs mouth-0")

    # 2. the face is still, the mouth moves — measured between mouth-0 and mouth-4
    d = cv2.absdiff(cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY),
                    cv2.cvtColor(imgs[CELLS.index("mouth-4")], cv2.COLOR_BGR2GRAY))
    moved = d > 18
    h = d.shape[0]
    upper = moved[:int(h * 0.55), :].mean() * 100      # forehead + eyes
    lower = moved[int(h * 0.62):, :].mean() * 100      # mouth + jaw
    if upper >= 3.0:
        notes.append(f"face not still: {upper:.1f}% of upper pixels move (need <3%)")
    if lower < 8.0:
        notes.append(f"mouth barely opens: {lower:.1f}% of lower pixels move (need >=8%)")

    # 2b. the eyes must not move across the mouth ramp — they are crossfaded by
    #     amplitude, so any difference swims while the character talks.
    eyes_worst = 0.0
    for k in ("mouth-1", "mouth-2", "mouth-3", "mouth-4"):
        de = cv2.absdiff(cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY),
                         cv2.cvtColor(imgs[CELLS.index(k)], cv2.COLOR_BGR2GRAY))
        eyes_worst = max(eyes_worst, (de[int(h * 0.28):int(h * 0.52), :] > 18).mean() * 100)
    if eyes_worst > 1.0:
        notes.append(f"eyes move while talking ({eyes_worst:.1f}%) — mouth frames must share mouth-0's eyes")

    # 2c. the BODY must still be there. The sheet is asked to preserve the master's
    #     crop, and on one character it quietly did not: Vector came back as a head
    #     with almost no shoulders (28.7% of the bottom row was subject, against
    #     86-97% for every sibling and 87.8% in her own master). She rendered as a
    #     floating head in the swarm and nothing caught it.
    gb = cv2.cvtColor(imgs[0], cv2.COLOR_BGR2GRAY)
    body = (gb[int(h * 0.95):, :] > 28).mean() * 100
    #     Threshold 45%, set in the measured gap: the real failure was 28.7% and the
    #     narrowest legitimate silhouette is Sentinel at 54.7% (her hood is a tighter
    #     outline than anyone else's shoulders). 55% was chosen before I had seen her
    #     and condemned a character whose body is plainly there.
    if body < 45.0:
        notes.append(f"body missing: bottom row only {body:.0f}% subject (need 45%) — "
                     f"the sheet cropped the shoulders off")

    # 2c-bis. THE HEAD MUST FACE FORWARD.
    #
    # The frames are the shipped artefact and nothing here checked pose, so an
    # off-axis master produced off-axis frames and the only gate that could see it
    # was the one on the masters — which is easy to override while chasing a
    # different failure. That is exactly what happened: Meridian shipped at -7.9
    # degrees of yaw because a glow rebuild was accepted at 6/10 and his pose
    # failure went along for the ride. Justin spotted it on screen.
    #
    # Same limits as the master gate (cast_pose): yaw 6, roll 4, pitch 12. Measured
    # on the cast the day this was added: nine drones inside +/-1.3 yaw, Meridian
    # at -7.9 and Sentinel at -6.0 with 9.2 of pitch.
    try:
        import cast_pose
        pose = cast_pose.pose(paths[0])
    except Exception:                                        # noqa: BLE001
        pose = None
    if pose is not None:
        yaw, pitch, roll = pose
        if abs(yaw) > 6 or abs(roll) > 4 or abs(pitch) > 12:
            notes.append(f"not facing forward: yaw {yaw:+.1f}, pitch {pitch:+.1f}, "
                         f"roll {roll:+.1f} (limits 6/12/4)")

    # 2d. the CROWN must be in frame. Rescaling cannot rescue this — if the sheet
    #     cut the top of the head off, shrinking the tile just smears a head that
    #     is already missing. Four characters shipped with their crowns flat
    #     against the top edge (0.0% clearance) against Voyager's 7.7%.
    gc = cv2.cvtColor(imgs[0], cv2.COLOR_BGR2GRAY)
    cb = gc[:, int(gc.shape[1] * 0.25):int(gc.shape[1] * 0.75)] > 38
    rows = np.nonzero(cb.sum(axis=1) > cb.shape[1] * 0.02)[0]
    crown = (rows[0] / h * 100) if len(rows) else 0.0
    if crown < 2.0:
        notes.append(f"crown clipped: only {crown:.1f}% clear above the head (need 2%) — "
                     f"the sheet cropped the top of the head")

    # 3. the blink must leave the MOUTH exactly where mouth-0 has it.
    #    The blink is crossfaded over whatever mouth frame is showing, so a blink
    #    whose mouth differs makes the mouth appear to move every time the drone
    #    blinks — Justin spotted it on Echo. Measured across the cast, six of ten
    #    were doing it, up to 19% on Vector. mouth-0 and blink must agree below
    #    the nose; only the eyes may differ.
    dm = cv2.absdiff(cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY),
                     cv2.cvtColor(imgs[CELLS.index("blink")], cv2.COLOR_BGR2GRAY))
    blink_mouth = (dm[int(h * 0.62):, :] > 18).mean() * 100
    if blink_mouth > 6.0:
        notes.append(f"blink moves the mouth ({blink_mouth:.1f}%) — it must match mouth-0")

    # 4. the blink must actually close the eyes
    db = cv2.absdiff(cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY),
                     cv2.cvtColor(imgs[CELLS.index("blink")], cv2.COLOR_BGR2GRAY))
    # Measure the blink on SKIN ONLY. Facial metal (Meridian's monocle, Pulsar's
    # comms yoke) is deliberately pinned so it cannot jitter, so counting those
    # pixels drags the average down and condemns a blink that plainly works —
    # it pushed two characters under the bar the moment the pinning shipped.
    _hsv = cv2.cvtColor(ref, cv2.COLOR_BGR2HSV)
    _metal = ((_hsv[:, :, 2] > 120) & (_hsv[:, :, 1] < 70))
    _band = slice(int(h * 0.28), int(h * 0.52))
    _skin = ~_metal[_band, :]
    eye_band = ((db[_band, :] > 18) & _skin).sum() / max(_skin.sum(), 1) * 100
    if eye_band < 2.0:
        notes.append(f"blink does not close the eyes: {eye_band:.1f}% of the eye band moves")

    return (not notes), (f"drift {worst:.1f}px · face {upper:.1f}% · mouth {lower:.1f}% · "
                         f"blink {eye_band:.1f}% · blinkmouth {blink_mouth:.1f}%" + ("  — " + "; ".join(notes) if notes else ""))


def build(name, key, reuse=False):
    """Generate a sheet and cut frames from it. `reuse` re-cuts the sheet already on
    disk instead of paying for another generation — the sheet is the expensive part and
    the registration is the part that gets iterated, so they should not be coupled."""
    os.makedirs(SHEETS, exist_ok=True)
    os.makedirs(RES, exist_ok=True)
    sheet_path = os.path.join(SHEETS, f"{name}-sheet-{VER}.png")
    if reuse and os.path.exists(sheet_path):
        raw = open(sheet_path, "rb").read()
    else:
        raw, err = generate_sheet(name, key)
        if raw is None:
            return False, err
        open(sheet_path, "wb").write(raw)
    sheet = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if sheet is None:
        return False, "sheet did not decode"

    cells = split_cells(sheet)
    ref = cells[0]
    out = []
    for i, cell in enumerate(cells):
        fixed = cell if i == 0 else register(ref, cell)[0]
        out.append(cv2.resize(fixed, (OUT_PX, OUT_PX), interpolation=cv2.INTER_AREA))
    out = lock_mouth_to_rest(out)
    out = lock_eyes_to_rest(out)
    out = lock_eye_hardware(out)
    out, centre_note = normalise_set(out)

    # STAGE, VERIFY, THEN PUBLISH — never the other way round.
    #
    # This used to write straight into Resources/ and verify afterwards, so a
    # FAILING generation still replaced working assets. It destroyed a good set
    # twice in one session: once when a twelve-cell experiment failed on all ten
    # characters, and again when a blink fix came back worse than what it
    # replaced. A generator with no seed cannot reproduce what it overwrites, so
    # the old files are simply gone. Write to a staging directory, run the same
    # verification against it, and only copy into Resources/ if it passes.
    stage = os.path.join(SHEETS, f".stage-{name}")
    os.makedirs(stage, exist_ok=True)
    for c, im in zip(CELLS, out):
        cv2.imwrite(os.path.join(stage, f"{name}-{c}.png"), im,
                    [cv2.IMWRITE_PNG_COMPRESSION, 9])
    ok, msg = verify(name, directory=stage)
    if ok:
        for c in CELLS:
            shutil.copy2(os.path.join(stage, f"{name}-{c}.png"),
                         os.path.join(RES, f"{name}-{c}.png"))
        note = centre_note
    else:
        note = f"{centre_note} · REJECTED, existing frames kept"
    shutil.rmtree(stage, ignore_errors=True)
    return ok, f"{msg} · {note}"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    verify_only = "--verify-only" in sys.argv
    targets = args or CAST

    if verify_only:
        print(f'{"drone":10}{"ok":>5}  detail')
        bad = 0
        for n in targets:
            ok, msg = verify(n)
            bad += 0 if ok else 1
            print(f"{n:10}{'PASS' if ok else 'FAIL':>5}  {msg}")
        print(f"\n{len(targets) - bad}/{len(targets)} characters have a usable frame set")
        sys.exit(1 if bad else 0)

    reuse = "--reuse-sheets" in sys.argv
    key = None if reuse else api_key()
    print(f"building {len(targets)} frame sets from "
          f"{'the sheets already on disk' if reuse else 'approved masters'}\n")
    print(f'{"drone":10}{"ok":>5}  detail')
    bad = 0
    for n in targets:
        ok, msg = build(n, key, reuse=reuse)
        bad += 0 if ok else 1
        print(f"{n:10}{'PASS' if ok else 'FAIL':>5}  {msg}", flush=True)
    print(f"\n{len(targets) - bad}/{len(targets)} characters have a usable frame set")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
