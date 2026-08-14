#!/usr/bin/env python3
"""True 3D head pose from MediaPipe face landmarks.

The previous heuristic inferred pose from the glowing irises and the skin extent
either side of them. It produced false failures whenever a bright piece of hardware
sat near an eye — it paired Pulsar's left iris with a highlight on his headset and
reported him turned 7.3 degrees when he was square to camera.

This uses the 478-point face mesh and the facial transformation matrix, so yaw,
pitch and roll are measured, not guessed.

  python3 scripts/cast_pose.py [version]
"""
import math
import os
import sys

import numpy as np

_LANDMARKER = None
MODEL = os.path.expanduser("~/.cache/mediapipe/face_landmarker.task")


def _landmarker():
    global _LANDMARKER
    if _LANDMARKER is None:
        from mediapipe.tasks import python as mpp
        from mediapipe.tasks.python import vision
        if not os.path.exists(MODEL):
            raise FileNotFoundError(
                f"face landmarker model missing at {MODEL} — download it from "
                "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
                "face_landmarker/float16/1/face_landmarker.task")
        opts = vision.FaceLandmarkerOptions(
            base_options=mpp.BaseOptions(model_asset_path=MODEL),
            output_facial_transformation_matrixes=True,
            num_faces=1)
        _LANDMARKER = vision.FaceLandmarker.create_from_options(opts)
    return _LANDMARKER


def pose(path):
    """Return (yaw, pitch, roll) in degrees, or None if no face is found.

    yaw   left/right turn   — 0 is square to camera
    pitch chin up/down      — 0 is level
    roll  head tilt         — 0 is upright
    """
    import mediapipe as mp
    res = _landmarker().detect(mp.Image.create_from_file(path))
    if not res.facial_transformation_matrixes:
        return None
    m = np.array(res.facial_transformation_matrixes[0]).reshape(4, 4)
    R = m[:3, :3]
    # ZYX Euler decomposition; guard the gimbal case
    sy = math.hypot(R[0, 0], R[1, 0])
    if sy < 1e-6:
        pitch = math.degrees(math.atan2(-R[1, 2], R[1, 1]))
        yaw = math.degrees(math.atan2(-R[2, 0], sy))
        roll = 0.0
    else:
        pitch = math.degrees(math.atan2(R[2, 1], R[2, 2]))
        yaw = math.degrees(math.atan2(-R[2, 0], sy))
        roll = math.degrees(math.atan2(R[1, 0], R[0, 0]))
    return yaw, pitch, roll


def eye_centres(path):
    """Iris centres in pixels, from the mesh rather than from the glow."""
    import mediapipe as mp
    img = mp.Image.create_from_file(path)
    res = _landmarker().detect(img)
    if not res.face_landmarks:
        return None
    lms = res.face_landmarks[0]
    H, W = img.height, img.width
    # 468-472 right iris, 473-477 left iris in the 478-point mesh
    if len(lms) < 478:
        return None
    r = np.mean([[lms[i].x * W, lms[i].y * H] for i in range(468, 473)], axis=0)
    l = np.mean([[lms[i].x * W, lms[i].y * H] for i in range(473, 478)], axis=0)
    return (tuple(l), tuple(r)) if l[0] < r[0] else (tuple(r), tuple(l))


def face_anchors(path):
    """Eye centres, nose tip and mouth centre — the four points a face is judged by.

    Interocular distance alone fixes face WIDTH and nothing else, so a longer or
    shorter face still reads as a different zoom even when the eyes match. Justin's
    instruction (2026-08-13): "Use eye, nose and mouth as a reference point for
    position, size & zoom of each face."

    Landmarks: irises 468-472 (right) and 473-477 (left), nose tip 1, mouth centre
    from the inner lip pair 13/14.
    """
    import mediapipe as mp
    img = mp.Image.create_from_file(path)
    res = _landmarker().detect(img)
    if not res.face_landmarks:
        return None
    lms = res.face_landmarks[0]
    if len(lms) < 478:
        return None
    H, W = img.height, img.width
    def pt(i):
        return np.array([lms[i].x * W, lms[i].y * H])
    def mean(ix):
        return np.mean([pt(i) for i in ix], axis=0)
    r = mean(range(468, 473))
    l = mean(range(473, 478))
    if l[0] > r[0]:
        l, r = r, l
    nose = pt(1)
    mouth = (pt(13) + pt(14)) / 2.0
    return np.array([l, r, nose, mouth], dtype=np.float64)


if __name__ == "__main__":
    VER = sys.argv[1] if len(sys.argv) > 1 else "v8"
    CAST = ["pulsar", "voyager", "sentinel", "nova", "nebula",
            "echo", "atlas", "iris", "meridian", "vector"]
    print(f"HEAD POSE — {VER}   (degrees; 0,0,0 is square to camera)")
    print(f'{"drone":10}{"yaw":>8}{"pitch":>8}{"roll":>8}   verdict')
    for n in CAST:
        p = f"generated-images/{n}-android-{VER}-aligned.png"
        if not os.path.exists(p):
            print(f"{n:10}  missing")
            continue
        r = pose(p)
        if r is None:
            print(f"{n:10}  no face detected")
            continue
        y, pi, ro = r
        bad = abs(y) > 6 or abs(ro) > 4 or abs(pi) > 12
        print(f"{n:10}{y:>8.1f}{pi:>8.1f}{ro:>8.1f}   "
              f'{"** OFF-AXIS **" if bad else "frontal"}')
