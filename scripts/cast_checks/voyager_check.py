"""LINEAGE — is this derived asset actually derived from the master it names?

Voyager's lens: asset and record integrity.

Every aligned PNG carries an `ArchivalOriginal` tEXt chunk written by
cast-provenance.py, naming the archival master it was cut from. Nothing has ever
checked that the claim is true. The generator takes no seed, so a re-render is a
DIFFERENT FACE — and the failure mode is silent: cast-build.py re-renders only the
characters that failed, and if the archive step and the align step land either side
of that re-render, the aligned PNG and its master are two different people wearing
the same name. Observed live on 2026-08-13: pulsar's raw render (18:50), archived
master (18:46) and aligned derivative (18:49) were three different byte streams.

This measures the thing itself — shared pixel provenance — not a proxy for it.
Timestamps, file sizes and manifest hashes all describe the record; SIFT
correspondence under a RANSAC-fitted similarity describes the IMAGE. Two crops of
one render share hundreds of geometrically consistent keypoints. Two renders of the
same prompt share almost none, because the model drew a new face.

THRESHOLD PROVENANCE — measured across all nine of the v8 cast:
    true lineage (aligned vs its own master)     344 - 1062 inliers  (weakest: pulsar 344)
    same character, different render (v7 raw)      2 -   13 inliers  (strongest: echo 13)
    same character, different render (v6 raw)      2 -   13 inliers  (strongest: echo 13)
    a different character's master                 3 -   25 inliers  (strongest: pulsar/voyager 25)
MIN_INLIERS = 60 sits 5.7x below the weakest true match and 2.4x above the loudest
false one. The gap is two orders of magnitude wide; the line is not delicate.

Fails loudly and never silently passes: a missing pointer, a missing master, an
unreadable file or an unavailable feature detector are all failures, because in each
case the lineage is unproven — which is the same operational state as being broken.
"""
import os

import cv2
import numpy as np

NAME = "lineage"

MIN_INLIERS = 60      # see THRESHOLD PROVENANCE above
WORK_PX = 800         # both images normalised to this long edge before matching
RANSAC_PX = 3.0       # reprojection tolerance for the fitted similarity


def _gray(path):
    im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if im is None:
        return None
    s = WORK_PX / max(im.shape[:2])
    return cv2.resize(im, (max(1, int(im.shape[1] * s)), max(1, int(im.shape[0] * s))),
                      interpolation=cv2.INTER_AREA)


def _archival_pointer(path):
    """The master this asset claims, read from its own PNG tEXt chunks."""
    from PIL import Image
    with Image.open(path) as im:
        return (getattr(im, "text", {}) or {}).get("ArchivalOriginal")


def check(img, path, rgb):
    cv2.setRNGSeed(20260813)          # RANSAC is stochastic; the gate must not be

    try:
        pointer = _archival_pointer(path)
    except Exception as e:
        return 0.0, False, f"lineage unreadable ({e})"
    if not pointer:
        return 0.0, False, "no archival pointer in asset"

    master = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(path)), pointer))
    if not os.path.exists(master):
        return 0.0, False, f"archival master missing ({os.path.basename(master)})"

    a, b = _gray(path), _gray(master)
    if a is None or b is None:
        return 0.0, False, "lineage unmeasurable (image unreadable)"

    try:
        sift = cv2.SIFT_create(nfeatures=2000)
    except Exception as e:
        return 0.0, False, f"lineage unmeasurable (no detector: {e})"

    ka, da = sift.detectAndCompute(a, None)
    kb, db = sift.detectAndCompute(b, None)
    if da is None or db is None or len(ka) < 10 or len(kb) < 10:
        return 0.0, False, "lineage unmeasurable (too few features)"

    # Lowe ratio test, then a similarity fit. The RANSAC step is what makes this a
    # lineage measure rather than a texture-similarity one: the surviving matches
    # must agree on ONE crop-and-scale, which only holds if the pixels are the same
    # pixels. Unstructured matches between two different faces do not survive it.
    pairs = cv2.BFMatcher().knnMatch(da, db, k=2)
    good = [m for m, n in (p for p in pairs if len(p) == 2) if m.distance < 0.75 * n.distance]
    if len(good) < 4:
        return 0.0, False, f"derived from a different render ({len(good)} matches)"

    src = np.float32([ka[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kb[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    _, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC,
                                          ransacReprojThreshold=RANSAC_PX)
    inliers = float(mask.sum()) if mask is not None else 0.0

    if inliers < MIN_INLIERS:
        return inliers, False, (f"asset drifted from its master "
                                f"{os.path.basename(master)} ({inliers:.0f} inliers)")
    return inliers, True, ""
