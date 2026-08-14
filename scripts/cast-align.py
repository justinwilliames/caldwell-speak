"""Register the cast on their glowing irises.

  python3 scripts/cast-align.py [version]
"""
import cv2, numpy as np, os, sys, colorsys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cast_pose
from PIL import Image

G = 'generated-images'
VER = sys.argv[1] if len(sys.argv) > 1 else 'v8'
OUT_SZ, IOD, EYE_CY = 1024, 0.166, 0.395
# ^ Voyager's measured framing, adopted as the cast reference on Justin's call
#   (2026-08-13): "zoom everyone in so they are the same size/crop as Voyager...
#   I don't care what gets cropped on their gear / bust."
#   EYE_CY moved 0.366 -> 0.395 after the scale law changed: matching whole-face
#   size zooms short-faced characters IN, which clipped four crowns. Dropping the
#   shared eye line buys every character the same extra headroom without breaking
#   the shared-eye-line property that makes them read as one shoot.

# PER-CHARACTER SCALE, not one global scale.
#
# The aligner used to pick a single scale for the whole cast — the tightest that
# kept EVERY crown inside the frame — so the unit with the tallest headgear
# (a hood, a helmet, big hair) dictated the zoom for all ten. Worse, a shared
# scale preserves whatever head size the GENERATOR happened to produce, so the
# output IODs still ranged 12.3%-17.7%: Atlas read tiny and Vector read close.
# Scaling each character to the same interocular distance is what actually makes
# them match, and it costs only the crown margin — which we are told not to care
# about.
GLOBAL_SCALE_MODE = False
# Mean distance of the four facial anchors from their centroid, as a fraction
# of frame width. Measured on Voyager — the character Justin named as the
# framing reference — at his approved crop.
ANCHOR_RADIUS = 0.1006
CROWN_MARGIN = 0.045   # only consulted when GLOBAL_SCALE_MODE is on
CROWN_Y = 0.055   # crown sits this far down the frame
# ONE SOURCE OF TRUTH FOR COLOUR — see the same note in cast-gate.py. This file
# used to carry its own hardcoded copy of the palette; when the cast moved onto a
# new palette, that copy and the gate's copy were both left behind and agreed with
# each other, so nothing noticed. Load the assignment instead.
def _load_locked_colours():
    import json as _json
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, "drone-forge", "current-assignment.json")) as f:
        asg = _json.load(f)
    return {n: tuple(int(h.lstrip("#")[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
            for n, h in asg.items()}


HUE = _load_locked_colours()
CAST = list(HUE)


def eye_pair_mesh(path):
    """Iris centres from the MediaPipe face mesh — exact, and immune to the bright
    hardware that defeated the glow-blob pairing (Voyager returned no pair at all)."""
    try:
        return cast_pose.eye_centres(path)
    except Exception:
        return None


def eye_pair_pts(img, rgb):
    H, W = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_t = colorsys.rgb_to_hsv(*rgb)[0] * 179.0
    hd = np.minimum(np.abs(hsv[:, :, 0].astype(float) - h_t), 179 - np.abs(hsv[:, :, 0].astype(float) - h_t))
    # bright + saturated + near the character's own hue
    mask = ((hsv[:, :, 2] > 170) & (hsv[:, :, 1] > 70) & (hd < 28)).astype(np.uint8)
    band = np.zeros_like(mask)
    band[int(H * .18):int(H * .70), int(W * .18):int(W * .82)] = 1
    mask = cv2.morphologyEx(mask * band, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(mask, 8)
    blobs = []
    for i in range(1, n):
        a = st[i, cv2.CC_STAT_AREA]
        bw, bh = st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]
        if a < 30 or bh == 0:
            continue
        # an iris is compact and roughly round; a lit seam is long and thin
        if not (0.4 <= bw / bh <= 2.5):
            continue
        if a < 0.25 * bw * bh:          # reject sparse/streaky components
            continue
        blobs.append((cen[i][0], cen[i][1], a, bw))
    best, score = None, -1e9
    for i in range(len(blobs)):
        for j in range(i + 1, len(blobs)):
            a, b = blobs[i], blobs[j]
            d = abs(a[0] - b[0])
            if not (W * 0.10 < d < W * 0.42):        # plausible interocular distance
                continue
            if abs(a[1] - b[1]) > H * 0.035:          # same height
                continue
            big, small = max(a[2], b[2]), min(a[2], b[2])
            if big > small * 4:                       # eyes are similar in size
                continue
            mid = (a[0] + b[0]) / 2
            # prefer a pair spaced like real eyes over merely the biggest pair
            s = (-abs(d - 0.20 * W) * 3.0
                 - abs(mid - W / 2) * 0.9
                 - abs(a[1] - b[1]) * 2.0
                 + (a[2] + b[2]) ** 0.5 * 2.0)
            if s > score:
                score, best = s, sorted([(a[0], a[1]), (b[0], b[1])])
    return best


def crown_of(img):
    """Topmost row of the subject in the central band."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    H, W = g.shape
    cen = g[:, int(W * .28):int(W * .72)] > 34
    hit = np.nonzero(cen.sum(axis=1) > (W * 0.44) * 0.03)[0]
    return int(hit[0]) if len(hit) else 0


# PASS 1 — what scale can each character take before its crown leaves the frame?
# The whole cast then uses the tightest scale that still works for everyone, so the
# heads share one size AND no head is ever cut.
caps = []
for _n in CAST:
    _img = cv2.imread(f'{G}/{_n}-android-{VER}.png')
    if _img is None:
        continue
    _p = eye_pair_mesh(f'{G}/{_n}-android-{VER}.png') or eye_pair_pts(_img, HUE[_n])
    if _p is None:
        continue
    (_lx, _ly), (_rx, _ry) = _p
    _iod = np.hypot(_rx - _lx, _ry - _ly)
    _my = (_ly + _ry) / 2
    _crown = crown_of(_img)
    # eye-to-crown distance in source pixels; needs to fit above EYE_CY minus the margin
    _above = max(_my - _crown, 1)
    _cap = ((EYE_CY - CROWN_MARGIN) * OUT_SZ) / _above
    caps.append(min((IOD * OUT_SZ) / _iod, _cap))
GLOBAL_SCALE = min(caps) if caps else None
if GLOBAL_SCALE:
    print(f'{VER}: one global scale {GLOBAL_SCALE:.4f} — tightest that keeps every crown in frame')
if not GLOBAL_SCALE_MODE:
    GLOBAL_SCALE = None
    print(f'{VER}: per-character scale — every face normalised to IOD {IOD:.3f}, '
          f'eye line {EYE_CY:.3f} (Voyager\'s framing)')

print(f'{VER}: registering on glowing irises')
print(f'{"drone":10}{"IOD%":>8}{"eyeCy%":>9}  pad(l,t,r,b)')
fails = []
for n in CAST:
    src = f'{G}/{n}-android-{VER}.png'
    img = cv2.imread(src)
    if img is None:
        # A member with no render must NOT take the cast down with it. This crashed
        # the aligner on the tenth drone, which left the other nine holding stale
        # aligned frames — and the gate then reported the whole cast as failing
        # lineage and provenance. One absent character is one absent row.
        print(f"{n:10}  no render — skipped")
        continue
    p = eye_pair_mesh(src) or eye_pair_pts(img, HUE[n])
    if p is None:
        print(f'{n:10}  NO VALID EYE PAIR — refusing to guess'); fails.append(n); continue
    (lx, ly), (rx, ry) = p
    iod = np.hypot(rx - lx, ry - ly)
    mx, my = (lx + rx) / 2, (ly + ry) / 2

    # SCALE ON THE WHOLE FACE, NOT ON EYE SPACING ALONE.
    #
    # Interocular distance fixes face WIDTH and nothing else. Measured across the
    # cast it varied only 7% while eye-to-mouth distance varied 22% — so faces that
    # matched perfectly on eye spacing still read at visibly different zooms, which
    # is exactly what Justin kept seeing. Scale instead on the mean radius of the
    # four facial anchors (both eyes, nose tip, mouth centre) about their centroid:
    # a single number that carries face width AND face length, which is what a
    # person means by "the same zoom".
    s = None
    if not GLOBAL_SCALE:
        a = cast_pose.face_anchors(src)
        if a is not None:
            rad = float(np.mean(np.linalg.norm(a - a.mean(axis=0), axis=1)))
            if rad > 1:
                s = (ANCHOR_RADIUS * OUT_SZ) / rad
                # Re-centre on the anchor centroid's eye row so the eye line still
                # lands where the framing law puts it.
                mx, my = float((a[0][0] + a[1][0]) / 2), float((a[0][1] + a[1][1]) / 2)
    if s is None:
        s = GLOBAL_SCALE if GLOBAL_SCALE else (IOD * OUT_SZ) / iod
    H, W = img.shape[:2]
    im2 = cv2.resize(img, (int(round(W * s)), int(round(H * s))), interpolation=cv2.INTER_LANCZOS4)
    sh, sw = im2.shape[:2]
    cx, cy = mx * s, my * s
    # Vertical anchor: blend the eye line with the CROWN so head size variation
    # does not drift the head up and down the frame. Eye-line alone put Sentinel's
    # crown at 22.9% against a cast median of 2.8%.
    gs = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    sh2, sw2 = gs.shape
    band = gs[:, int(sw2 * .25):int(sw2 * .75)] > 38
    rs = band.sum(axis=1)
    hit = np.nonzero(rs > sw2 * 0.02)[0]
    crown = int(hit[0]) if len(hit) else int(cy - 0.22 * OUT_SZ)
    want_eye = cy - EYE_CY * OUT_SZ          # where the eye rule wants the crop top
    want_crown = crown - CROWN_Y * OUT_SZ    # where the crown rule wants it
    # Anchor vertically on the EYE LINE, not the crown.
    #
    # Crown anchoring kept every head fully in frame, but it made the eye line ride
    # with hair and headgear height — the cast spanned 32.9% to 42.6%, so faces sat
    # at visibly different heights and the portraits did not read as one shoot.
    # Justin's call (2026-08-13): match Voyager's crop, "I don't care what gets
    # cropped on their gear / bust". A shared eye line is what makes ten portraits
    # look like ten photographs taken on the same day, and the cost is the top of a
    # hood or a tall haircut — which is the cheaper thing to lose.
    top = want_eye if not GLOBAL_SCALE_MODE else crown_of(im2) - CROWN_MARGIN * OUT_SZ
    left = cx - OUT_SZ / 2
    pl, pt = max(0, int(np.ceil(-left))), max(0, int(np.ceil(-top)))
    pr, pb = max(0, int(np.ceil(left + OUT_SZ - sw))), max(0, int(np.ceil(top + OUT_SZ - sh)))
    if pl or pt or pr or pb:
        ring = np.concatenate([im2[:6].reshape(-1, 3), im2[-6:].reshape(-1, 3),
                               im2[:, :6].reshape(-1, 3), im2[:, -6:].reshape(-1, 3)])
        lum = ring.astype(int).sum(axis=1)
        fill = np.median(ring[lum <= np.percentile(lum, 25)], axis=0)
        im2 = cv2.copyMakeBorder(im2, pt, pb, pl, pr, cv2.BORDER_CONSTANT, value=[float(v) for v in fill])
    L, T = int(round(left)) + pl, int(round(top)) + pt
    out = f'{G}/{n}-android-{VER}-aligned.png'
    cv2.imwrite(out, im2[T:T + OUT_SZ, L:L + OUT_SZ])
    q = eye_pair_mesh(out) or eye_pair_pts(cv2.imread(out), HUE[n])
    if q:
        (a, b), (c, d) = q
        print(f'{n:10}{100*np.hypot(c-a,d-b)/OUT_SZ:>7.1f}%{100*((b+d)/2)/OUT_SZ:>8.1f}%  ({pl},{pt},{pr},{pb})')
    else:
        print(f'{n:10}   (recheck failed)          ({pl},{pt},{pr},{pb})')
print('\nfailed:', fails or 'none')
