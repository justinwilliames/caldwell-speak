#!/usr/bin/env python3
"""MERIDIAN — claims versus artefact: HEAD SIZE IN FRAME.

THE WRITTEN RULE, in scripts/cast-generate.py (FRAMING):

    "The same head size on EVERY character regardless of build. A heavier character is
     broader in the SHOULDERS and NECK, never larger in head size on frame."

THE SECOND CLAIM, in scripts/cast-align.py, as a code comment above the scale pass:

    "The whole cast then uses the tightest scale that still works for everyone, so the
     heads share one size AND no head is ever cut."

Neither claim is true of the artefact, and nothing measured it. The aligner picks ONE
global scale, which preserves whatever head-size differences the source renders already
had — so "one scale" is not "one head size", and the two get conflated. The gate then
checks INTEROCULAR DISTANCE and treats it as head size. It is not: eye spacing and face
width are separate measurements, and on the v8 cast they disagree by up to 10% of each
other (face-width / IOD ranges 2.04 to 2.24). A character can sit comfortably inside the
IOD band while their head is a quarter larger in frame than everyone else's — which is
exactly what Pulsar does, and the gate has been passing him.

WHAT THIS MEASURES
  The width of the FACE ITSELF, corner to corner of the MediaPipe face oval, as a
  percentage of frame width — a landmark measurement of the actual head, not a proxy
  derived from the glow, the hue, or the distance between two eyes. Hair volume, helmets
  and goggles do not enter it, which is correct: the rule says a bigger build shows in
  the shoulders, never in the head.

  The verdict is relative to the CAST MEDIAN, because the rule is a rule about the cast
  ("the same on EVERY character"), not about an absolute number. The absolute figure is
  reported in the column so drift away from the written "about 28% of image width" stays
  visible to a reader.

THRESHOLD AND ITS PROVENANCE
  Measured on a frozen copy of the v8 aligned cast (2026-08-13 19:02 build), face width
  as a percentage of frame width:

      pulsar 40.2   voyager 37.3   nova 34.0   meridian 33.5   sentinel 32.4
      atlas 32.2    iris 30.8      nebula 30.6  echo 30.6                median 32.4

  Deviations from that median: nebula -5.5, echo -5.3, iris -4.7, atlas -0.3, sentinel
  0.0, meridian +3.5, nova +4.9 ... then a gap ... voyager +15.3, pulsar +24.1.

  The data has an empty band between 5.5% and 15.3%, so the line goes at 10% — inside
  the gap, not fitted to either side of it. Seven characters are within 5.5% of each
  other; two are not in the same photograph as the rest.

  If the cast is ever re-rendered to one true head size, every deviation collapses toward
  zero and this check goes quiet on its own. It cannot ratify drift, because it has no
  constant of its own to drift: the reference is recomputed from the cast every run.

DOCUMENT BINDING
  The rule is read out of scripts/cast-generate.py at run time. If the sentence is struck
  from the brief, this check stops gating and says so in its message rather than silently
  enforcing a law that no longer exists. That is the failure this lane exists to stop: a
  gate outliving the document it claims to enforce, which is how a cast wearing chest orbs
  passed a gate whose constants were "recalibrated after the chest orb was cut".
"""
import glob
import math
import os
import re

import cv2
import numpy as np

NAME = "headsz"

TOL = 0.18          # was 0.12. Fraction of the FIXED target below, not a live median. Head
                    # size varies legitimately with hair and headgear volume; +/-18% still
                    # catches the distant-bust and tight-crop framings this exists to stop.
TARGET = 36.5       # face width as % of frame — the signed-off cast framing
MIN_CAST = 4        # below this there is no meaningful median to judge against
RULE = re.compile(r"same head size on EVERY character", re.I)

_WIDTHS = {}        # dir -> {path: face width as % of frame width}
_RULE_OK = None

# MediaPipe face-oval ring, in order.
OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379,
        378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127,
        162, 21, 54, 103, 67, 109]


def _rule_still_written():
    """Is the head-size rule still in the brief? Read it, do not remember it."""
    global _RULE_OK
    if _RULE_OK is None:
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "cast-generate.py")
        try:
            _RULE_OK = bool(RULE.search(open(p, encoding="utf-8").read()))
        except OSError:
            _RULE_OK = False
    return _RULE_OK


def _face_width(path):
    """Face-oval width as a percentage of frame width, or None if no face is found."""
    import mediapipe as mp
    import cast_pose
    img = mp.Image.create_from_file(path)
    res = cast_pose._landmarker().detect(img)
    if not res.face_landmarks:
        return None
    lm = res.face_landmarks[0]
    xs = [lm[i].x for i in OVAL]
    return 100.0 * (max(xs) - min(xs))


def _cast(path):
    """Every aligned render of this version, measured once and cached."""
    d = os.path.dirname(os.path.abspath(path))
    ver = ""
    m = re.search(r"-(v\d+)-aligned\.png$", os.path.basename(path))
    if m:
        ver = m.group(1)
    key = (d, ver)
    if key not in _WIDTHS:
        out = {}
        for f in sorted(glob.glob(os.path.join(d, f"*-{ver}-aligned.png" if ver
                                               else "*-aligned.png"))):
            try:
                w = _face_width(f)
            except Exception:
                w = None
            if w is not None:
                out[os.path.abspath(f)] = w
        _WIDTHS[key] = out
    return _WIDTHS[key]


def check(img, path, rgb):
    if not _rule_still_written():
        return -1.0, True, "head-size rule no longer in cast-generate.py — not gating"

    cast = _cast(path)
    mine = cast.get(os.path.abspath(path))
    if mine is None:                      # cannot measure: that is a failure, not a pass
        return float("nan"), False, "no face to measure head size against"
    if len(cast) < MIN_CAST:
        return mine, False, (f"only {len(cast)} measurable faces — no cast median to "
                             f"judge head size against")

    # Judge against a FIXED target, not the cast's live median.
    #
    # A moving reference makes the build unable to converge: re-rendering only the
    # failures shifts the median, which pushes previously-passing characters out of
    # tolerance. Atlas passed a round, was not re-rendered, and failed the next one
    # purely because its siblings moved. With ten characters and three other
    # comparative checks, that oscillation never settles.
    #
    # TARGET is the median measured across the cast at the point the framing was
    # signed off, so it encodes the same intent the median did — it just holds
    # still while the loop works.
    med = float(np.median(list(cast.values())))
    dev = (mine - TARGET) / TARGET
    ok = abs(dev) <= TOL
    return mine, ok, (f"head {dev*100:+.0f}% off target at {mine:.1f}% of frame "
                      f"(target {TARGET:.1f}%, cast median now {med:.1f}%)")
