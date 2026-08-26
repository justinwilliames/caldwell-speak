"""Brand colour fidelity — does the rendered accent hue match the locked hex?

Every other hue-aware routine in this gate (eye_pair, the chest-orb mask, the
background-chroma check) SELECTS pixels using the character's own locked hue as the
search criterion, then reports on what it found. That is circular for a colour-match
check: you cannot prove the accent is on-hue by only ever looking where the target
hue already is. A drone rendered 30 degrees off its lock still gets a mask full of
"matching" pixels, because the mask was drawn around whatever hue is actually there
within a generous +-30 tolerance (see hue_mask's tol=30 in cast-gate.py) — that
tolerance alone would pass this exact failure mode.

This check selects independently of the target: any pixel that is bright and
saturated enough to read as an intentional accent/emissive colour (not blocked by
which hue it happens to be), takes the smoothed mode of that population's hue, and
only THEN compares it to the locked hex. A first pass using a looser S>90,V>170
gate pulled in warm key-lit skin and swamped the real accent on three characters
(sentinel's peak landed at hue 26 — skin — instead of 204, its actual armour cyan
sitting at 691 px was outvoted by 8500+ px of face). Tightening to S>120,V>220
drops skin out of the population on every character tested while keeping enough
accent/emissive pixels to find a stable peak; the result held under a
neighbouring parameter sweep (S>110,V>210 and S>130,V>225 moved every character's
answer by under 2 degrees).
"""
import colorsys

import cv2
import numpy as np

NAME = "hue_fid"

S_MIN, V_MIN = 120, 220   # accent/emissive pixels; skin falls out below this (see above)
MIN_PX = 40                # below this the population is too thin to trust a mode
SMOOTH_K = 7                # circular smoothing window on the 360-bin hue histogram

# Threshold provenance: measured on the full v8 cast at S>120,V>220 (2026-08-13).
# Eight of nine characters landed within 1.2-18.2 degrees of their locked hue
# (pulsar was the outlier at 18.2, likely just a thin-sample case at n=155px).
# meridian landed at 32.0 degrees (peak hue 187, cyan, against a locked navy at
# 219) and held at 32-33 degrees across every parameter variant tried. 25 degrees
# sits in the gap between the worst legitimate character (18.2) and the one that
# is actually wrong (32), with margin on both sides.
MAX_HUE_DRIFT_DEG = 25.0


def check(img, path, rgb):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    mask = (hsv[:, :, 1] > S_MIN) & (hsv[:, :, 2] > V_MIN)
    n = int(mask.sum())
    target_hue = colorsys.rgb_to_hsv(*rgb)[0] * 360.0

    if n < MIN_PX:
        # Fail loudly: no accent population found is not evidence of a match.
        return float("nan"), False, f"hue_fid: only {n}px bright+saturated enough to judge"

    h_px = (hsv[:, :, 0][mask] * 2.0).astype(np.int32) % 360  # OpenCV H (0-179) -> degrees
    hist = np.bincount(h_px, minlength=360).astype(np.float64)
    k = SMOOTH_K
    padded = np.concatenate([hist[-k:], hist, hist[:k]])
    smoothed = np.convolve(padded, np.ones(k), mode="same")[k:-k]
    actual_hue = float(np.argmax(smoothed))

    diff = abs(actual_hue - target_hue)
    diff = min(diff, 360.0 - diff)

    ok = diff <= MAX_HUE_DRIFT_DEG
    msg = f"hue_fid: accent {actual_hue:.0f} deg vs locked {target_hue:.0f} deg ({diff:.1f} off, n={n})"
    return diff, ok, msg
