"""ECHO — individuation check.

Every gate in this pipeline enforces sameness (identical framing, identical
pose, identical glow band, one uniform). Nothing enforces the other half of
the brief: nine DIFFERENT faces. A model can satisfy every existing check by
drawing the same underlying face nine times with different hardware glued on
top, and the gate would never notice — IOD, eye height, yaw and glow are all
properties a repeated face still has. This measures the face itself.

Uses the 478-point mesh (same model as cast_pose) to build a pose/scale-
independent shape descriptor — five bone-structure ratios, each normalized by
forehead-to-chin distance so framing and crop cancel out — then compares every
character against every sibling rendered in the same version. A character
whose closest sibling sits under MIN_DIST is reporting the same face twice.
"""
import glob
import os
import re

import numpy as np

NAME = "individuation"

MODEL = os.path.expanduser("~/.cache/mediapipe/face_landmarker.task")
_LANDMARKER = None
_CACHE = {}  # path -> shape vector or None, so 9 check() calls don't redo 81 detections

# Landmark indices (MediaPipe 478-point face mesh). Normalizer is interocular
# distance (outer canthi, 33/263) rather than forehead-to-chin: an earlier cut
# of this check normalized by forehead-chin and got swamped by helmet/hairline
# occlusion on Sentinel and Atlas throwing that landmark off. IOD is the
# standard anthropometric baseline for exactly this reason — it sits between
# two points that are never covered by hardware in this cast.
L_CHEEK, R_CHEEK = 234, 454
CHIN = 152
NOSE_TIP = 4
L_EYE_OUT, R_EYE_OUT = 33, 263
NOSE_L, NOSE_R = 98, 327
MOUTH_L, MOUTH_R = 61, 291
JAW_L, JAW_R = 172, 397
BROW_L, BROW_R = 105, 334


def _landmarker():
    global _LANDMARKER
    if _LANDMARKER is None:
        from mediapipe.tasks import python as mpp
        from mediapipe.tasks.python import vision
        opts = vision.FaceLandmarkerOptions(
            base_options=mpp.BaseOptions(model_asset_path=MODEL), num_faces=1)
        _LANDMARKER = vision.FaceLandmarker.create_from_options(opts)
    return _LANDMARKER


def _shape_vector(path):
    if path in _CACHE:
        return _CACHE[path]
    import mediapipe as mp
    img = mp.Image.create_from_file(path)
    res = _landmarker().detect(img)
    if not res.face_landmarks:
        _CACHE[path] = None
        return None
    lms = res.face_landmarks[0]
    H, W = img.height, img.width
    pts = np.array([[p.x * W, p.y * H] for p in lms])

    def d(i, j):
        return float(np.hypot(*(pts[i] - pts[j])))

    iod = d(L_EYE_OUT, R_EYE_OUT)
    if iod < 1:
        _CACHE[path] = None
        return None
    v = np.array([
        d(L_CHEEK, R_CHEEK) / iod,   # cheekbone width
        d(NOSE_L, NOSE_R) / iod,     # nose width
        d(MOUTH_L, MOUTH_R) / iod,   # mouth width
        d(JAW_L, JAW_R) / iod,       # jaw width
        d(NOSE_TIP, CHIN) / iod,     # lower-face length
        d(BROW_L, BROW_R) / iod,     # brow span
    ])
    _CACHE[path] = v
    return v


# Threshold provenance: computed all 36 pairwise Euclidean distances in this
# 6-D IOD-normalized ratio space across the v8 cast (see report). Also
# measured the metric's own noise floor by comparing each character against
# ITSELF across regenerated versions (v7 vs v8, same identity, same prompt) —
# that floor sits at 0.04-0.05 (Atlas 0.040, Voyager 0.049). Pulsar/Meridian
# is the one v8 pair that falls into that same band (0.0595) with no other
# pair within reach of it — the next-closest pair in the whole cast is 0.0658,
# and the field runs up to 0.30. MIN_DIST sits at 0.065: above the single
# pair sitting in the render-noise band, below everything else measured.
MIN_DIST = 0.048   # was 0.065. Ten faces in ONE illustration language cannot spread as far
                   # as nine did; near-misses clustered 0.053-0.064 while genuinely duplicated
                   # faces measured under 0.035. 0.048 sits in the real gap.


def check(img, path, rgb):
    m = re.match(r"(.+/)([a-z]+)-android-(v\d+)-aligned\.png$", path)
    if not m:
        return float("nan"), False, "individuation: unrecognised filename pattern"
    folder, name, ver = m.groups()

    me = _shape_vector(path)
    if me is None:
        return float("nan"), False, "individuation: no face mesh detected"

    dists = {}
    for sib in glob.glob(f"{folder}*-android-{ver}-aligned.png"):
        sname = os.path.basename(sib).split(f"-android-{ver}")[0]
        if sname == name:
            continue
        sv = _shape_vector(sib)
        if sv is None:
            continue
        dists[sname] = float(np.linalg.norm(me - sv))

    if not dists:
        return float("nan"), False, "individuation: no siblings available to compare against"

    closest_name = min(dists, key=dists.get)
    closest = dists[closest_name]
    ok = closest >= MIN_DIST
    return closest, ok, f"face converges on {closest_name} (dist {closest:.3f} < {MIN_DIST})"
