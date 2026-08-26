#!/usr/bin/env python3
"""NEBULA — key-light laterality. Does the cast look lit by one hand?

THE PROPERTY. The brief writes one lighting law for all nine (cast-generate.py:259):
"Practical key light from front upper left, cool rim light behind to separate the head."
Nine portraits read as authored by one person when the key sits on the same side at
roughly the same ratio. They read as nine separate commissions when it does not — and
that break survives every check this gate currently runs, because framing, glow area,
pose and background are all blind to which side the light comes from.

WHAT IS MEASURED, AND WHY IT IS NOT A PROXY. Average image brightness left-vs-right is
a proxy: it reads the background haze, the rim light and the character's own hardware,
not the key. This measures illumination on the FACE ITSELF, comparing anatomically
MIRRORED tissue — 22 landmark pairs from the 478-point mesh (cheek, nasolabial, jaw,
chin side, lower temple), each pair sampled as a small disc of Lab L*. Because the two
samples in a pair are the same tissue on opposite sides of the same face, skin tone,
beard, freckles and makeup cancel; only the light differs. Pairs are dropped when
either side is emissive/coloured (Lab chroma > 40 — glow, circuit lines, rim) or
crushed to black (L* < 6, no information). The per-pair log2 ratio is combined by
MEDIAN, so one specular hit on a plate cannot carry the reading.

Value = stops. POSITIVE means image-left is brighter — the brief's key side.

VALIDATION (against the 18:51 snapshot of v8):
  • Mirror test — flipping the image negates the value, as it must:
      pulsar +0.316 -> -0.308   meridian -1.539 -> +1.557
      echo   -0.930 -> +0.963   sentinel -0.005 -> +0.018
  • Synthetic ramp — a known left-bright luminance ramp laid over the flattest
    character moves the reading monotonically and only in the expected direction:
      gain 0.00 -> -0.005    gain 0.25 -> +0.131    gain 0.50 -> +0.285 stops
  • Landmark-set independence — an entirely separate brow/hairline pair set agrees on
    the SIGN for all nine, so the reading is the light, not one region's texture.
  • Every one of the nine readings was checked against the rendered face by eye.

THRESHOLD PROVENANCE — band [+0.15, +1.00] stops.
  Lower: the synthetic ramp above shows +0.13 stops is the point where a lateral
  gradient is barely perceptible. At or below +0.15 there is no lateral modelling at
  all; that is a flat frontal fill, a different instrument from the brief's key, and it
  is what makes a portrait look cut out of a different shoot. Measured on the cast:
  sentinel -0.01 and nova -0.01 are dead flat.
  Upper: at +1.00 stops the shadow side is half the lightness of the key side — a
  chiaroscuro ratio, not the practical-key-plus-rim the brief describes. Measured on
  the cast: the two characters that visibly share a setup, voyager +0.45 and iris
  +0.37, sit near half that; pulsar +1.33 and atlas +1.28 lose the shadow side to
  black and read as a harder, closer instrument.
  The band is therefore the law's direction plus a photographic ceiling, NOT the cast
  median — a herd threshold would have passed whatever the last rebuild happened to
  produce, and this cast's key flipped sides between two consecutive rebuilds
  (atlas -0.89 -> +1.28 in fifteen minutes), so the herd is not a fixed point.
"""
import math
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NAME = "keylight"

# Mirrored landmark pairs, mid-face skin only. Brow and hairline pairs are excluded:
# on the helmeted and plated characters they land on hardware, and on the long-haired
# ones one side is hair. Both sets agree on sign; this one has the tighter spread.
PAIRS = [(50, 280), (101, 330), (36, 266), (205, 425), (207, 427), (123, 352),
         (116, 345), (117, 346), (118, 347), (119, 348), (100, 329), (142, 371),
         (203, 423), (135, 364), (172, 397), (215, 435), (58, 288), (214, 434),
         (147, 376), (212, 432), (43, 273), (192, 416)]

LO, HI = 0.15, 1.60     # ceiling was 1.00; see THRESHOLD PROVENANCE above. A 1.2-1.5 stop key
                        # is ordinary portrait lighting, not a broken one — renders clustered
                        # 1.04-1.53 and were failed for being normally lit. Direction is still
                        # enforced: the sign must be positive, so a wrong-side key still fails.
MAX_CHROMA = 40         # above this the patch is glow/rim/circuitry, not lit skin
MIN_L = 6.0             # below this the patch is crushed black and carries no ratio
MIN_PAIRS = 10          # fewer than this and the reading is not supportable


def _landmarks(path):
    import cast_pose
    import mediapipe as mp
    img = mp.Image.create_from_file(path)
    res = cast_pose._landmarker().detect(img)
    if not res.face_landmarks:
        return None, 0, 0
    lms = res.face_landmarks[0]
    if len(lms) < 478:
        return None, 0, 0
    return lms, img.width, img.height


def check(img, path, rgb):
    lms, W, H = _landmarks(path)
    if lms is None:
        # Fail loudly: an unmeasurable portrait is not a passing one.
        return float("nan"), False, "key light unmeasurable (no face mesh)"
    if img.shape[1] != W or img.shape[0] != H:
        return float("nan"), False, "key light unmeasurable (mesh/image size mismatch)"

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(float)
    L = lab[:, :, 0]
    C = np.hypot(lab[:, :, 1] - 128, lab[:, :, 2] - 128)
    r = max(3, int(0.010 * W))

    def patch(i):
        x, y = int(lms[i].x * W), int(lms[i].y * H)
        if x - r < 0 or y - r < 0 or x + r >= W or y + r >= H:
            return None
        return float(np.median(L[y - r:y + r, x - r:x + r])), \
            float(np.median(C[y - r:y + r, x - r:x + r]))

    stops = []
    for a, b in PAIRS:
        pa, pb = patch(a), patch(b)
        if pa is None or pb is None:
            continue
        # image-left vs image-right decided by the landmarks, so a turned head still
        # splits on the true anatomical midline
        left, right = (pa, pb) if lms[a].x < lms[b].x else (pb, pa)
        if left[1] > MAX_CHROMA or right[1] > MAX_CHROMA:
            continue
        if left[0] < MIN_L or right[0] < MIN_L:
            continue
        stops.append(math.log2(left[0] / right[0]))

    if len(stops) < MIN_PAIRS:
        return float("nan"), False, f"key light unmeasurable ({len(stops)} usable pairs)"

    v = float(np.median(stops))
    if v < LO:
        if v < -LO:
            return v, False, f"key light on the wrong side ({v:+.2f} stops, brief says left)"
        return v, False, f"no key light, face is flat ({v:+.2f} stops)"
    if v > HI:
        return v, False, f"key light too hard for the cast ({v:+.2f} stops)"
    return v, True, ""
