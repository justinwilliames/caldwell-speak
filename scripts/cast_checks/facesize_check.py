"""FACESIZE — is every face actually the same size in frame?

THE PROPERTY. Justin, 2026-08-13: "zoom everyone in so they are the same size/crop as
Voyager" and then, when it still looked uneven, "Use eye, nose and mouth as a reference
point for position, size & zoom of each face."

That second instruction is the whole check. The cast used to be scaled on INTEROCULAR
DISTANCE, which fixes face WIDTH and nothing else. Measured across the ten:

    interocular distance   166-178 px      7% variation
    eye-to-mouth distance  172-209 px     22% variation

So ten faces could match perfectly on eye spacing and still read at visibly different
zooms, because a long face at the same eye spacing is a bigger face. Justin saw it; the
gate could not, because nothing measured whole-face size.

MEASURED. The mean distance of four facial anchors — both iris centres, the nose tip and
the mouth centre — from their own centroid, as a fraction of frame width. One number that
carries width AND length. Landmarks come from the 478-point MediaPipe mesh via
cast_pose.face_anchors(), the same source the aligner scales on, so the check and the
transform agree about what a face is.

Note this is deliberately NOT a second opinion on the aligner's arithmetic — it cannot be,
since both read the same landmarks. It catches the case the aligner cannot: a render whose
face the mesh reads differently after alignment, and any future change that silently stops
applying the anchor scale at all.

THRESHOLD PROVENANCE — target 0.1006, tolerance +/-8%.

  The target is Voyager's own anchor radius at the crop Justin approved as the reference:
  103.0 px of 1024 = 0.1006 of frame width.

  Measured across the cast immediately after the anchor scale was wired in:

      meridian 0.0998   nebula 0.0999   nova 0.1005   echo 0.1004   sentinel 0.1009
      vector   0.1010   atlas  0.1012   pulsar 0.1013  voyager 0.1015  iris 0.1016

  Spread 0.0998-0.1016 = 1.8%. Tolerance is set at 8% — four times the achieved spread —
  because the aligner already holds this tightly by construction, so the check's job is to
  catch a REGRESSION, not to police the last percent. A tolerance near the achieved spread
  would fire on ordinary landmark jitter and teach everyone to ignore it.
"""
import numpy as np

NAME = "facesize"

TARGET = 0.1006     # Voyager's anchor radius as a fraction of frame width
TOL = 0.08          # +/- 8%; see provenance above


def check(img, path, rgb):
    try:
        import cast_pose
    except ImportError:
        return float("nan"), False, "facesize: cast_pose unavailable"
    if img is None:
        return float("nan"), False, "facesize: no image"

    a = cast_pose.face_anchors(path)
    if a is None:
        return float("nan"), False, "facesize: no face mesh — cannot measure face size"

    w = img.shape[1]
    radius = float(np.mean(np.linalg.norm(a - a.mean(axis=0), axis=1))) / w
    dev = (radius - TARGET) / TARGET
    ok = abs(dev) <= TOL
    return radius, ok, (f"face is {dev*100:+.0f}% off the cast size at {radius:.4f} "
                        f"(target {TARGET:.4f}, measured on eyes+nose+mouth)")
