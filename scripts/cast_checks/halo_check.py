"""HALO — is the background the SAME kind of black-plus-glow on every character?

THE PROPERTY. Justin, 2026-08-14: "make sure all backgrounds are consistent —
they should be black with their colour glow and nothing more."

Two separate things have to hold, and only one of them was ever measured. The
existing `bgvar` check asks whether the background is FLAT (no scenery, no
panelling), and the cast passes it comfortably — variance 4.8 to 7.9. What nothing
asked was whether the glow on that flat black is the same STRENGTH and the right
COLOUR from one character to the next.

Measured across the ten before this check existed:

    halo saturation   voyager  54   meridian  59   vector  61
                      pulsar  151   nebula   156   atlas  159
                      nova    162   sentinel 170   iris   192   echo  206

    hue error vs the locked colour
                      iris    136 deg      meridian  46 deg
                      atlas    20 deg      sentinel  18 deg      rest under 15

So three characters sit at roughly a third the glow strength of the top three —
side by side that reads as some portraits being lit and others not — and Iris's
halo is not her colour at all: 136 degrees off is most of the way round the wheel.

MEASURED. The halo is the background (outside a closed subject mask) that still
carries light: luminance above 10 but below the subject threshold. Saturation is
its mean; hue error is the circular distance from the locked colour's hue. Corner
luminance is checked separately — the far corners must actually be black, because
a glow that reaches the frame edge is a wash, not a halo.

THRESHOLD PROVENANCE.
  Saturation band 90-210. The cast's own middle six sit 151-192, which is the look
  that was signed off; 90 excludes the three washed-out units without being so
  tight that ordinary variation trips it, and 210 stops a saturated flood.
  Hue error 25 degrees, matching `hue_fid`'s tolerance for the lit elements — the
  background spill is the same colour claim as the irises and should be held to
  the same standard.
  Corner luminance 18. The cast measures 0.3-10.4, so 18 leaves real headroom and
  only fires when the glow has genuinely reached the corners.
"""
import json
import os

import cv2
import numpy as np

NAME = "halo"

SAT_MIN, SAT_MAX = 90.0, 210.0
HUE_TOL = 25.0
CORNER_MAX = 18.0
SUBJECT_LUMA = 28
GLOW_LUMA = 10


def _locked_hue(name):
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with open(os.path.join(root, "drone-forge", "current-assignment.json")) as f:
        hexv = json.load(f)[name].lstrip("#")
    bgr = np.uint8([[[int(hexv[4:6], 16), int(hexv[2:4], 16), int(hexv[0:2], 16)]]])
    return float(cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)[0, 0, 0]) * 2


def check(img, path, rgb):
    if img is None:
        return float("nan"), False, "halo: no image"
    name = os.path.basename(path).split("-android-")[0]
    try:
        want = _locked_hue(name)
    except (KeyError, OSError, ValueError):
        return float("nan"), False, "halo: no locked colour for this character"

    h, w = img.shape[:2]
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    subject = cv2.morphologyEx((grey > SUBJECT_LUMA).astype(np.uint8),
                               cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    background = subject == 0
    halo = background & (grey > GLOW_LUMA)
    if halo.sum() < 200:
        return 0.0, False, "no coloured glow behind the character at all"

    sat = float(hsv[:, :, 1][halo].mean())
    hues = hsv[:, :, 0][halo].astype(float) * 2
    err = float(min(abs(np.median(hues) - want), 360 - abs(np.median(hues) - want)))

    c = int(h * 0.09)
    corner = np.zeros_like(background)
    corner[:c, :c] = corner[:c, -c:] = corner[-c:, :c] = corner[-c:, -c:] = True
    corner &= background
    corner_v = float(grey[corner].mean()) if corner.sum() else 0.0

    notes = []
    if sat < SAT_MIN:
        notes.append(f"glow too weak (saturation {sat:.0f}, need {SAT_MIN:.0f})")
    elif sat > SAT_MAX:
        notes.append(f"glow too strong (saturation {sat:.0f}, max {SAT_MAX:.0f})")
    if err > HUE_TOL:
        notes.append(f"glow is the wrong colour ({err:.0f} deg off the locked hue)")
    if corner_v > CORNER_MAX:
        notes.append(f"glow reaches the corners (luminance {corner_v:.0f}) — "
                     f"it should fade to black well before the frame edge")

    return sat, (not notes), ("; ".join(notes) if notes
                              else f"sat {sat:.0f}, hue {err:.0f} deg off, corners {corner_v:.0f}")
