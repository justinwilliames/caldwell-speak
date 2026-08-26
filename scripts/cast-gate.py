#!/usr/bin/env python3
"""Cast gate — checks the rendered cast against its own written laws.

Prompts have repeatedly failed to hold framing, hue, glow and the chest core, so
these are enforced here after render rather than requested before it. Exits
non-zero on any failure so a build step can depend on it.

  python3 scripts/cast-gate.py [version]      # default v8
"""
import colorsys
import math
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VER = sys.argv[1] if len(sys.argv) > 1 else "v8"
G = "generated-images"

# Locked brand colours, mirroring DroneRegistry.swift
# ONE SOURCE OF TRUTH FOR COLOUR.
#
# This table used to be a hardcoded copy of the palette, and cast-align.py held a
# second copy. When the cast moved onto a new palette both copies were left behind,
# so `hue_fid` cheerfully gated every drone against a hex that existed in neither
# DroneRegistry.swift nor the assignment file — two stale copies agreeing with each
# other and calling it a pass. Sentinel and Voyager found it independently in the
# same review, which is how you know it was invisible rather than unlikely.
#
# Colour now loads from drone-forge/current-assignment.json, which is also what the
# briefs and the Swift registry are generated against. A stale copy cannot drift if
# there is no copy.
def _load_locked_colours():
    import json as _json
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "drone-forge", "current-assignment.json")
    with open(path) as f:
        asg = _json.load(f)
    out = {}
    for name, hexv in asg.items():
        h = hexv.lstrip("#")
        out[name] = tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return out


HUE = _load_locked_colours()

IOD_TARGET, IOD_TOL = 17.5, 4.5        # LOOSE SANITY BAND ONLY — no longer the scale law.
                                       # The cast is scaled on the four-anchor radius (eyes,
                                       # nose, mouth), because interocular distance fixes face
                                       # WIDTH alone: it varied 7% across the cast while
                                       # eye-to-mouth varied 22%, so faces matched on IOD and
                                       # still read at different zooms. Scaling on whole-face
                                       # size necessarily spreads IOD — a short face at the
                                       # same overall size has wider-set eyes as a fraction of
                                       # frame. Gating IOD tightly would now condemn correctly
                                       # scaled faces. The real check is `facesize` in
                                       # cast_checks/, which measures the anchor radius itself.
EYE_CY_TARGET, EYE_CY_TOL = 36.0, 8.0  # was 37.0/6.0. Crown-anchored placement puts taller
                                       # hair volumes near 30%; +/-8 still catches a genuinely
                                       # mis-framed eye line without punishing big hair.
GLOW_MIN, GLOW_MAX = 0.04, 1.60        # ceiling was 1.20. Nebula's design is legitimately the
                                       # most luminous in the cast and sat at 1.23; the runaway
                                       # blooms this guards against measured 2.1-4.5.
ORB_MIN_PX = 400                       # size at which a sternum emitter is recorded as an orb
EYE_MIN_V = 175                        # was 200. Observed lit irises land 179-249; 200 sat
                                       # inside the normal band and failed genuinely-glowing
                                       # eyes. A dim tinted lens still measures well under 175.
YAW_MAX_DEG = 6.0                      # left/right head turn, degrees
PITCH_MAX_DEG = 16.0                   # chin up/down, degrees
ROLL_MAX_DEG = 4.0                     # tilt of the line between the irises, degrees
# BACKGROUND GATE — no scenes, no sets, no texture. A character sits on flat black
# with only their own colour hazing behind them. Two independent measures: chroma
# (is the black actually black?) and variance (is there structure in it?).
BG_MAX_CHROMA = 8                      # Lab chroma on dark corner pixels
BG_MAX_VAR = 14                        # luminance std behind the subject


def hue_mask(img, rgb, vmin=170, smin=60, tol=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_t = colorsys.rgb_to_hsv(*rgb)[0] * 179.0
    hd = np.abs(hsv[:, :, 0].astype(float) - h_t)
    hd = np.minimum(hd, 179 - hd)
    return ((hsv[:, :, 2] > vmin) & (hsv[:, :, 1] > smin) & (hd < tol)).astype(np.uint8)


def eye_pair(img, rgb):
    H, W = img.shape[:2]
    m = hue_mask(img, rgb)
    band = np.zeros_like(m)
    band[int(H * .18):int(H * .70), int(W * .18):int(W * .82)] = 1
    m = cv2.morphologyEx(m * band, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, _, st, cen = cv2.connectedComponentsWithStats(m, 8)
    blobs = []
    for i in range(1, n):
        a, bw, bh = st[i, cv2.CC_STAT_AREA], st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]
        if a < 30 or bh == 0 or not (0.4 <= bw / bh <= 2.5) or a < 0.25 * bw * bh:
            continue
        blobs.append((cen[i][0], cen[i][1], a))
    best, score = None, -1e9
    for i in range(len(blobs)):
        for j in range(i + 1, len(blobs)):
            a, b = blobs[i], blobs[j]
            d = abs(a[0] - b[0])
            if not (W * 0.10 < d < W * 0.42) or abs(a[1] - b[1]) > H * 0.035:
                continue
            # Irises are a MATCHED pair. A bright highlight on hardware is not:
            # it differs in size and sits off-centre. Both caught false pairs on
            # Pulsar and Voyager before these two constraints were added.
            big, small = max(a[2], b[2]), max(min(a[2], b[2]), 1)
            if big / small > 2.2:
                continue
            if abs((a[0] + b[0]) / 2 - W / 2) > W * 0.06:
                continue
            s = -abs(d - 0.20 * W) * 3 - abs((a[0] + b[0]) / 2 - W / 2) * .9 + (a[2] + b[2]) ** .5 * 2
            if s > score:
                score, best = s, (d, (a[1] + b[1]) / 2)
    return best


def head_pose_true(path):
    """True 3D head pose via MediaPipe face mesh — see scripts/cast_pose.py.

    Replaces a heuristic that inferred pose from the glowing irises and skin extent.
    That version paired an iris with a hardware highlight and reported Pulsar turned
    7.3 deg and Voyager 21.2 deg when both measure square to camera.
    """
    try:
        import cast_pose
        return cast_pose.pose(path)
    except Exception:
        return None


def check(name):
    p = f"{G}/{name}-android-{VER}-aligned.png"
    img = cv2.imread(p)
    if img is None:
        return {"drone": name, "fail": ["missing render"]}
    H, W = img.shape[:2]
    rgb = HUE[name]
    fails, vals = [], {}

    # one source of truth for eye geometry: the same mesh the pose check uses
    ep = None
    try:
        import cast_pose
        ec = cast_pose.eye_centres(p)
        if ec:
            (lx, ly), (rx, ry) = ec
            ep = (math.hypot(rx - lx, ry - ly), (ly + ry) / 2)
    except Exception:
        ep = None
    if ep is None:
        ep = eye_pair(img, rgb)
    if ep is None:
        fails.append("no eye pair")
        vals["iod"] = vals["cy"] = float("nan")
    else:
        d, cy = ep
        vals["iod"] = 100 * d / W
        vals["cy"] = 100 * cy / H
        if abs(vals["iod"] - IOD_TARGET) > IOD_TOL:
            fails.append(f"IOD {vals['iod']:.1f}%")
        if abs(vals["cy"] - EYE_CY_TARGET) > EYE_CY_TOL:
            fails.append(f"eyeCy {vals['cy']:.1f}%")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    em = (hsv[:, :, 2] > 200) & (hsv[:, :, 1] > 90)
    vals["glow"] = 100 * em.sum() / em.size
    if not (GLOW_MIN <= vals["glow"] <= GLOW_MAX):
        fails.append(f"glow {vals['glow']:.2f}%")

    # Chest orbs are PERMITTED (Justin, 2026-08-13, reversing the earlier cut). They
    # are measured for the record but never gate: an orb may sit anywhere, including
    # partly outside the crop, and must not influence framing.
    chest = img[int(H * .70):, :]
    n, _, st, cen = cv2.connectedComponentsWithStats(hue_mask(chest, rgb), 8)
    orb = 0
    for i in range(1, n):
        a = st[i, cv2.CC_STAT_AREA]
        bw, bh = st[i, cv2.CC_STAT_WIDTH], max(st[i, cv2.CC_STAT_HEIGHT], 1)
        if a < ORB_MIN_PX or not (0.6 <= bw / bh <= 1.7):
            continue
        if not (38 <= 100 * cen[i][0] / W <= 62):
            continue
        orb = max(orb, a)
    vals["core"] = orb
    # measured only; an orb is not a failure

    # Background tint: measured as Lab chroma on genuinely dark pixels in the TOP
    # corners only. HSV saturation is unusable here (near-black pixels report wild
    # saturation), and the side/bottom edges are shoulder, not background.
    t = int(H * .18)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    corners = np.concatenate([lab[:t, :t].reshape(-1, 3), lab[:t, -t:].reshape(-1, 3)])
    dark = corners[corners[:, 0] < 90]
    if len(dark) < 50:
        dark = corners
    chroma = np.hypot(dark[:, 1].astype(float) - 128, dark[:, 2].astype(float) - 128)
    vals["bg"] = float(np.percentile(chroma, 90))
    # A coloured glow behind the character is explicitly allowed, so chroma alone is
    # not a failure — only scenery is. Recorded for reference.

    # Background STRUCTURE: an environment behind the subject defeats iris
    # registration (a lit bulkhead offers competing bright blobs) and cannot be held
    # identical across six unseeded lip-sync frames. Team ruling 2026-08-13: none.
    top = cv2.cvtColor(img[:int(H * .30)], cv2.COLOR_BGR2GRAY)
    side = np.concatenate([top[:, :int(W * .20)].ravel(), top[:, int(W * .80):].ravel()])
    vals["bgvar"] = float(side.std())
    if vals["bgvar"] > BG_MAX_VAR:
        fails.append(f"background has scenery ({vals['bgvar']:.0f})")

    try:
        import cast_pose
        ec = cast_pose.eye_centres(p)
    except Exception:
        ec = None
    if ec:
        hsv_full = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        vs = []
        for (ex, ey) in ec:
            r = max(4, int(0.012 * W))
            patch = hsv_full[max(0, int(ey) - r):int(ey) + r, max(0, int(ex) - r):int(ex) + r]
            if patch.size:
                vs.append(float(np.percentile(patch[:, :, 2], 85)))
        vals["eyeV"] = min(vs) if vs else 0.0
        if vals["eyeV"] < EYE_MIN_V:
            fails.append(f"eyes dim ({vals['eyeV']:.0f})")
    else:
        vals["eyeV"] = float("nan")

    pz = head_pose_true(p)
    if pz is None:
        vals["yaw"] = vals["pitch"] = vals["roll"] = float("nan")
        fails.append("no face for pose")
    else:
        vals["yaw"], vals["pitch"], vals["roll"] = pz
        if abs(vals["yaw"]) > YAW_MAX_DEG:
            fails.append(f"turned {vals['yaw']:+.1f} deg")
        if abs(vals["roll"]) > ROLL_MAX_DEG:
            fails.append(f"tilted {vals['roll']:+.1f} deg")
        if abs(vals["pitch"]) > PITCH_MAX_DEG:
            fails.append(f"chin {vals['pitch']:+.1f} deg")

    d = open(p, "rb").read()
    if b"trainedAlgorithmicMedia" not in d:
        fails.append("no provenance")

    for mod in globals().get("PLUGINS", []):
        try:
            value, ok, msg = mod.check(img, p, rgb)
            vals[mod.NAME] = value
            if not ok:
                fails.append(msg)
        except Exception as e:
            fails.append(f"{mod.NAME} errored: {e}")

    return {"drone": name, "fail": fails, **vals}


def load_plugins():
    """Load team-authored checks from scripts/cast_checks/.

    The Pulsar team can author gates directly rather than proposing them: any module
    here exposing NAME and check(img, path, rgb) -> (value, ok, message) is run against
    every character. They have caught this gate measuring the wrong thing three times,
    so the checks they write carry the same weight as the built-in ones.
    """
    import importlib.util
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cast_checks")
    out = []
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if not f.endswith(".py") or f.startswith("_"):
            continue
        try:
            sp = importlib.util.spec_from_file_location(f[:-3], os.path.join(d, f))
            m = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(m)
            if hasattr(m, "check") and hasattr(m, "NAME"):
                out.append(m)
        except Exception as e:
            print(f"  ! plugin {f} failed to load: {e}")
    return out


PLUGINS = load_plugins()
if PLUGINS:
    print(f"team-authored checks loaded: {', '.join(p.NAME for p in PLUGINS)}\n")

rows = [check(n) for n in HUE]
print(f"CAST GATE — {VER}")
print(f'{"drone":10}{"IOD%":>7}{"eyeCy%":>8}{"glow%":>8}{"yaw":>7}{"roll":>6}{"eyeV":>7}{"orb":>7}  result')
for r in rows:
    if "iod" not in r:
        print(f'{r["drone"]:10}  {", ".join(r["fail"])}')
        continue
    status = "PASS" if not r["fail"] else "FAIL: " + ", ".join(r["fail"])
    print(f'{r["drone"]:10}{r["iod"]:>7.1f}{r["cy"]:>8.1f}{r["glow"]:>8.2f}'
          f'{r.get("yaw", float("nan")):>7.1f}{r.get("roll", float("nan")):>6.1f}'
          f'{r.get("eyeV", float("nan")):>7.0f}{r.get("core", 0):>7.0f}  {status}')

bad = [r for r in rows if r["fail"]]
spread = [r["glow"] for r in rows if "glow" in r]
if spread:
    print(f'\nglow spread {max(spread)/max(min(spread), 1e-6):.1f}x  '
          f'(min {min(spread):.2f}%  max {max(spread):.2f}%)')
print(f'{len(rows)-len(bad)}/{len(rows)} pass')
sys.exit(1 if bad else 0)
