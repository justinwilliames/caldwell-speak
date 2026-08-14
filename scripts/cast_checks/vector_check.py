"""VECTOR — headroom. Is the top of the head actually inside the frame?

THE PROPERTY. Justin's call (2026-08-13): "the zoom is good — but make sure when
they are final that none of their head is cut off at the top. Design them as such."

Those two halves pull against each other, which is exactly why this needs measuring
rather than eyeballing. The cast is normalised to one zoom and one eye line
(cast-align.py: IOD 0.166, EYE_CY 0.366), so vertical placement is no longer free to
slide down and rescue a tall unit — the aligner used to be crown-anchored and that is
what made the eye line ride with hair height. With the eye line pinned, whether a
crown fits is decided by the SILHOUETTE ABOVE THE EYES, and that is a design property
of the character: hair volume, hood height, anything stacked on the skull. So it has
to be designed in, and this check is what tells you when it was not.

MEASURED. Scan down the middle half of the frame for the first row carrying a
meaningful amount of subject, and report it as a percentage of frame height. The
middle half only: a shoulder or a raised piece of kit at the frame edge is not the
crown, and including it would report headroom that the head does not have.

The subject threshold is luminance > 38 on a near-black void, the same figure the
aligner uses to find a crown, so the two agree about where a head starts.

THRESHOLD PROVENANCE — 2.0% of frame height, measured on the v8 cast at the
Voyager-normalised crop:

    clipped:  sentinel 0.0        (hood ran off the top edge)
    tight:    voyager 2.9   nebula 2.9
    clear:    iris 3.3   atlas 5.1   nova 5.3   pulsar 5.8   meridian 6.3
              vector 6.6   echo 8.3

A clipped crown measures 0.0 because the head is still cutting the top row. The
tightest character that still shows its whole head sits at 2.9. The bar goes at 2.0:
below it the head is touching or leaving the frame, above it there is real air. It is
deliberately NOT set at 2.9 — that would fail the two units Justin has already
approved, and a check that condemns the standard is measuring the wrong thing.
"""
import cv2
import numpy as np

NAME = "headroom"

MIN_CLEARANCE = 2.0     # % of frame height between the top edge and the crown
SUBJECT_LUMA = 38       # same subject threshold the aligner uses to find a crown
ROW_FRACTION = 0.02     # a row counts as subject once this much of the band is lit


def check(img, path, rgb):
    if img is None:
        return float("nan"), False, "headroom: no image"
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = g.shape
    # Middle half only — shoulders and side-mounted kit are not the crown.
    band = g[:, int(w * 0.25):int(w * 0.75)] > SUBJECT_LUMA
    bw = band.shape[1]
    rows = np.nonzero(band.sum(axis=1) > bw * ROW_FRACTION)[0]
    if not len(rows):
        return float("nan"), False, "headroom: no subject found in frame"

    clearance = float(rows[0]) / h * 100.0
    ok = clearance >= MIN_CLEARANCE
    if clearance <= 0.05:
        return clearance, False, ("head is CUT OFF at the top of the frame — the crown "
                                  "reaches the top edge")
    return clearance, ok, (f"only {clearance:.1f}% headroom above the crown "
                           f"(need {MIN_CLEARANCE:.1f}%)")
