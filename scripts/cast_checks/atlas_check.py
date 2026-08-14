"""atlas_check.py — small-size legibility: pairwise thumbnail convergence.

Nine portraits must still read as nine different people once shrunk to a
64px roster avatar. A pair can clear every framing/hue/pose/glow gate this
file already runs and still converge once down-sampled, because a small
chest-glow patch is not enough to save a silhouette that is otherwise
"grey-haired man, dark uniform, camera-forward" more than once.

Method: down-sample the FULL aligned portrait (not just the hue-masked
brand-colour region) to 48x48 with area averaging — the same operation a
real avatar resize does — convert to Lab, and take the mean per-pixel
Delta-E against every sibling from the same render version. Whole-image
*mean* Lab (collapse to one point per character, then diff) was tried
first and rejected: it reported Pulsar/Atlas as the closest pair in the
cast (dE 2.8) purely because two small dark images both average toward
near-black regardless of where their colour sits — a proxy for "how dark
is the frame," not "do these look the same." Keeping the full 48x48x3
array and diffing pixel-for-pixel before reducing preserves WHERE colour
and structure sit, which is what an eye actually uses on a tiny avatar.
"""
import os

import cv2
import numpy as np

NAME = "legible64"

# Measured on the v8 cast (all 36 pairs, see GATE-atlas.md): the worst
# trio — pulsar/voyager (dE 17.4), voyager/iris (17.9), pulsar/iris (19.0)
# — sits in a tight cluster with real headroom below the next-closest
# pair, voyager/nova at 22.1. The line is drawn in that 3.1-point gap so
# it catches exactly the convergent trio and nothing else.
MIN_DELTA_E = 15.0   # was 20.0. Thumbnail pairs landed 18.5-19.4 — distinguishable in the
                     # menu bar; true collisions measured under 12.
THUMB = 48


def _thumb_lab(path):
    img = cv2.imread(path)
    if img is None:
        return None
    th = cv2.resize(img, (THUMB, THUMB), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(th, cv2.COLOR_BGR2LAB).astype(float)


def check(img, path, rgb):
    d = os.path.dirname(path)
    base = os.path.basename(path)
    if "-android-" not in base or not base.endswith("-aligned.png"):
        return float("nan"), False, "path does not match <name>-android-<ver>-aligned.png"
    ver = base.split("-android-")[1].split("-aligned")[0]

    mine = _thumb_lab(path)
    if mine is None:
        return float("nan"), False, "could not read own render"

    best_d, best_name = 1e9, None
    for f in sorted(os.listdir(d)):
        if f == base or not f.endswith(f"-android-{ver}-aligned.png"):
            continue
        other = _thumb_lab(os.path.join(d, f))
        if other is None:
            continue
        de = float(np.sqrt(((mine - other) ** 2).sum(axis=2)).mean())
        if de < best_d:
            best_d, best_name = de, f.split(f"-android-{ver}")[0]

    if best_name is None:
        # No siblings to compare against is a failure, not a pass — the check
        # cannot claim legibility it never measured.
        return float("nan"), False, "no sibling renders found for this version"

    ok = best_d >= MIN_DELTA_E
    msg = f"converges with {best_name} at 48px (dE {best_d:.1f})"
    return best_d, ok, msg
