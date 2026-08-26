"""xreg — cross-validate the registration against a face-blind second opinion.

WHY THIS EXISTS
    Failure #1 of this gate was registration verifying its own output with the same
    detector that computed the transform: cast-align.py finds the irises with the
    MediaPipe mesh, warps on them, then re-runs the SAME mesh on its own output and
    prints the result as confirmation. cast-gate.py then measures IOD, eye height,
    iris brightness and head pose on that aligned frame with — again — the same mesh.
    One detector, one opinion, quoted three times. Nothing in the pipeline ever asks
    an independent instrument whether the aligned portrait is in fact a registration
    of the render it claims to come from.

    This check asks. It measures ONE quantity — the similarity transform from the
    master render to the aligned portrait — by two routes that share no code and no
    assumptions:

      face route   iris centres from the mesh on master vs on aligned  (what the
                   pipeline believes)
      scene route  SIFT keypoints + RANSAC over the whole frame, face-blind: it
                   knows nothing about eyes, heads, glow or hue

    When the two agree, every geometry column in the gate row rests on a transform
    two independent instruments confirm. When they disagree, the row is unverified —
    and the gate cannot tell you which instrument is lying, which is precisely the
    state it has reported as PASS three times.

WHAT IT CATCHES, IN ORDER OF HOW OFTEN IT BITES
    1. A STALE ALIGNED FRAME. cast-build.py re-renders only failures, and the raw and
       the aligned file are written by separate steps. If a character is re-rendered
       and not re-aligned, the gate happily measures yesterday's portrait and reports
       it as today's. The scene route collapses (few inliers) because the two files
       are no longer the same picture. Caught live on 2026-08-13 — see PROVENANCE.
    2. AN ALIGNED FRAME THAT IS NOT A SIMILARITY TRANSFORM of its master: a hand-edit,
       a crop, a re-touch, a file copied from the wrong character.
    3. MESH DRIFT. If the mesh lands on a different feature in the master than in the
       aligned frame, the face route and scene route disagree on where the eyes went.
       That is the failure-#1 signature, and it is invisible to a self-check.

THRESHOLD PROVENANCE  (measured 2026-08-13 on this cast)
    Twenty-four master/aligned pairs where the aligned frame genuinely derives from
    its master (all nine of v6, all nine of v7, the six settled units of v8):
        SIFT inlier ratio  0.93 – 0.99   (absolute inliers 332 – 1672)
        eye residual       0.5 – 4.2 %   of interocular distance
    Three v8 pairs whose raw render had been rewritten after the aligned frame:
        SIFT inlier ratio  0.14, 0.21, 0.24   (absolute inliers 6, 15, 12)
        eye residual       9.6 %, 2.7 %, 1.5 %
    MIN_INLIER_RATIO sits at 0.60 — the middle of a fourfold gap with nothing in it.
    MIN_INLIERS 50 is well under the worst corresponding pair (332) and well over the
    best broken one (15), so a low-texture frame cannot squeak through on a handful
    of matches. MAX_EYE_RESIDUAL 9.0 % is a little over twice the worst corresponding
    residual; it is the secondary condition and it is the one that caught Voyager.

    Note what these numbers also settle: the mesh's own IOD estimate moves by up to
    ~3 % between two framings of the same face. The gate's IOD tolerance (+/-3 points
    on a target of 16) is comfortably outside that noise, so that check is measuring
    framing and not detector jitter. Now demonstrated rather than assumed.

FAILS LOUDLY. No master on disk, no face in either file, too few matches to fit a
transform — all of those are failures. A measurement that cannot be made is not a pass.
"""
import math
import os

import cv2
import numpy as np

NAME = "xreg"

MIN_INLIERS = 50           # absolute; corresponding pairs run 332-1672, broken 6-15
MIN_INLIER_RATIO = 0.60    # corresponding 0.93-0.99, broken 0.14-0.24
MAX_EYE_RESIDUAL = 9.0     # % of interocular distance; corresponding max 4.2
WORK_W = 1000              # both frames scaled to this longest edge before matching
RATIO_TEST = 0.75          # Lowe
_SIFT = None


def _sift():
    global _SIFT
    if _SIFT is None:
        _SIFT = cv2.SIFT_create(nfeatures=4000)
    return _SIFT


def _master_for(path):
    """The render this aligned frame claims to be a registration of.

    Prefer the raw PNG cast-align.py actually reads; fall back to the archived master.
    """
    d, f = os.path.split(path)
    if f.endswith("-aligned.png"):
        raw = os.path.join(d, f[:-len("-aligned.png")] + ".png")
        if os.path.exists(raw):
            return raw
        stem = f[:-len("-aligned.png")]
        for cand in (os.path.join(d, "masters-archive", stem + "-master.jpg"),
                     os.path.join(d, "masters-archive", stem + "-master.png")):
            if os.path.exists(cand):
                return cand
    return None


def _scene_transform(src_path, dst_path):
    """Face-blind similarity fit src -> dst. Returns (M_in_full_res_terms, inliers, matches).

    M maps src full-resolution coordinates to dst full-resolution coordinates.
    """
    a = cv2.imread(src_path, cv2.IMREAD_GRAYSCALE)
    b = cv2.imread(dst_path, cv2.IMREAD_GRAYSCALE)
    if a is None or b is None:
        return None
    sa, sb = WORK_W / max(a.shape), WORK_W / max(b.shape)
    a2 = cv2.resize(a, None, fx=sa, fy=sa, interpolation=cv2.INTER_AREA)
    b2 = cv2.resize(b, None, fx=sb, fy=sb, interpolation=cv2.INTER_AREA)
    ka, da = _sift().detectAndCompute(a2, None)
    kb, db = _sift().detectAndCompute(b2, None)
    if da is None or db is None or len(ka) < 12 or len(kb) < 12:
        return None
    pairs = cv2.BFMatcher().knnMatch(da, db, k=2)
    good = [m for m, n in pairs if m.distance < RATIO_TEST * n.distance]
    if len(good) < 12:
        return None, 0, len(good)
    src = np.float32([ka[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kb[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    M, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC,
                                          ransacReprojThreshold=2.0, maxIters=5000)
    if M is None or mask is None:
        return None, 0, len(good)
    # rebase the fit from working-resolution to full-resolution coordinates
    F = np.array([[sa, 0, 0], [0, sa, 0], [0, 0, 1]])
    Mh = np.vstack([M, [0, 0, 1]])
    full = (np.diag([1 / sb, 1 / sb, 1.0]) @ Mh @ F)[:2]
    return full, int(mask.sum()), len(good)


def check(img, path, rgb):
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import cast_pose

    master = _master_for(path)
    if master is None:
        return 0.0, False, "xreg: no master render to cross-check the alignment against"

    fit = _scene_transform(master, path)
    if fit is None:
        return 0.0, False, "xreg: scene route could not read or describe the frames"
    M, inliers, matches = fit
    ratio = inliers / matches if matches else 0.0
    if M is None or inliers < MIN_INLIERS or ratio < MIN_INLIER_RATIO:
        return round(100 * ratio, 1), False, (
            f"aligned frame does not correspond to its master "
            f"({inliers}/{matches} inliers, {100*ratio:.0f}%) — the row measures a "
            f"picture the render no longer is")

    em, ea = cast_pose.eye_centres(master), cast_pose.eye_centres(path)
    if em is None or ea is None:
        return round(100 * ratio, 1), False, (
            f"xreg: face route found no irises on "
            f"{'the master' if em is None else 'the aligned frame'} — "
            f"the pipeline's own detector cannot be cross-checked")

    iod = math.hypot(ea[1][0] - ea[0][0], ea[1][1] - ea[0][1])
    if iod < 1:
        return round(100 * ratio, 1), False, "xreg: degenerate interocular distance"

    worst = 0.0
    for k in (0, 1):
        x, y = em[k]
        px = M[0, 0] * x + M[0, 1] * y + M[0, 2]
        py = M[1, 0] * x + M[1, 1] * y + M[1, 2]
        worst = max(worst, math.hypot(px - ea[k][0], py - ea[k][1]))
    resid = 100 * worst / iod

    if resid > MAX_EYE_RESIDUAL:
        return round(resid, 1), False, (
            f"registration self-confirms: face route and scene route disagree on where "
            f"the irises went by {resid:.1f}% of IOD (limit {MAX_EYE_RESIDUAL:.0f}%)")

    return round(resid, 1), True, ""
