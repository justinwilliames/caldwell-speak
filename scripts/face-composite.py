#!/usr/bin/env python3
"""Deterministically composite a real face photo onto a rendered scene.

Pipeline (no model drift, fully repeatable):
  1. Detect face + eye pair in BOTH the source photo and the destination render.
  2. Solve a similarity transform (scale + rotation + translation) that maps the
     source eye pair onto the destination eye pair.
  3. Warp the source photo into destination space.
  4. Build a feathered elliptical face mask sized to the destination face.
  5. Colour-match the source to the destination's local lighting in LAB.
  6. Poisson-blend (cv2.seamlessClone) so the seam disappears.
  7. Match film grain so the pasted region carries the same noise as the plate.

Usage: face_composite.py <dest.png> <source.jpg> <out.png> [--scale S] [--dy N]
"""
import sys, cv2, numpy as np

HAAR = cv2.data.haarcascades
FACE = cv2.CascadeClassifier(HAAR + "haarcascade_frontalface_alt2.xml")
EYE = cv2.CascadeClassifier(HAAR + "haarcascade_eye.xml")


def detect_face(gray):
    faces = FACE.detectMultiScale(gray, 1.08, 5, minSize=(40, 40))
    if not len(faces):
        raise SystemExit("no face detected")
    return max(faces, key=lambda f: f[2] * f[3])


def detect_eyes(gray, box):
    """Return (left_eye, right_eye) centres in image coords, screen-left first."""
    x, y, w, h = box
    # eyes live in the upper 60% of the face box
    roi = gray[y:y + int(h * 0.62), x:x + w]
    cands = EYE.detectMultiScale(roi, 1.06, 6,
                                 minSize=(max(8, int(w * 0.10)), max(8, int(w * 0.10))),
                                 maxSize=(int(w * 0.45), int(w * 0.45)))
    pts = [(x + ex + ew / 2.0, y + ey + eh / 2.0, ew * eh)
           for (ex, ey, ew, eh) in cands]
    if len(pts) >= 2:
        # prefer the pair that is most horizontal and widest apart
        best, score = None, -1e9
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                a, b = pts[i], pts[j]
                dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
                if dx < w * 0.15:
                    continue
                s = dx - 4 * dy + 0.001 * (a[2] + b[2])
                if s > score:
                    score, best = s, (a, b)
        if best:
            a, b = best
            return ((a[0], a[1]), (b[0], b[1])) if a[0] < b[0] else ((b[0], b[1]), (a[0], a[1]))
    # fallback: canonical eye positions for a frontal face box
    return ((x + w * 0.32, y + h * 0.40), (x + w * 0.68, y + h * 0.40))


def similarity(src_eyes, dst_eyes, extra_scale=1.0):
    (sl, sr), (dl, dr) = src_eyes, dst_eyes
    sv = np.array(sr) - np.array(sl)
    dv = np.array(dr) - np.array(dl)
    s = (np.linalg.norm(dv) / np.linalg.norm(sv)) * extra_scale
    ang = np.arctan2(dv[1], dv[0]) - np.arctan2(sv[1], sv[0])
    ca, sa = np.cos(ang) * s, np.sin(ang) * s
    smid = (np.array(sl) + np.array(sr)) / 2.0
    dmid = (np.array(dl) + np.array(dr)) / 2.0
    M = np.array([[ca, -sa, dmid[0] - (ca * smid[0] - sa * smid[1])],
                  [sa,  ca, dmid[1] - (sa * smid[0] + ca * smid[1])]], np.float32)
    return M


def face_mask(shape, box, feather_frac=0.07, grow=1.0):
    """Ellipse over the face: solid in the core, feathered only at the rim.

    A wide feather (the first attempt used 0.18) lets the plate underneath
    dominate the alpha blend and washes the real identity straight back out,
    so the default is deliberately tight.
    """
    x, y, w, h = box
    m = np.zeros(shape[:2], np.uint8)
    cx, cy = int(x + w / 2), int(y + h * 0.52)
    ax, ay = int(w * 0.44 * grow), int(h * 0.60 * grow)
    cv2.ellipse(m, (cx, cy), (ax, ay), 0, 0, 360, 255, -1)
    k = max(3, int(w * feather_frac) | 1)
    return cv2.GaussianBlur(m, (k, k), 0), (cx, cy)


def colour_match(src, dst, mask):
    """Shift src to dst's mean/std in LAB, inside the mask."""
    m = mask > 12
    if m.sum() < 50:
        return src
    s = cv2.cvtColor(src, cv2.COLOR_BGR2LAB).astype(np.float32)
    d = cv2.cvtColor(dst, cv2.COLOR_BGR2LAB).astype(np.float32)
    for c in range(3):
        sm, ss = s[:, :, c][m].mean(), s[:, :, c][m].std() + 1e-6
        dm, ds = d[:, :, c][m].mean(), d[:, :, c][m].std() + 1e-6
        s[:, :, c] = (s[:, :, c] - sm) * (ds / ss) + dm
    return cv2.cvtColor(np.clip(s, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)


def grain_of(img, box):
    """Estimate the plate's luminance noise sigma from FLAT skin, not hair.

    Sampling above the head catches hair and background detail and reads that
    edge energy as noise (it returned 5.4 and visibly speckled the face). The
    cheek band is flat, so its residual is closer to true sensor grain.
    """
    x, y, w, h = box
    patch = img[y + int(h * 0.45):y + int(h * 0.70), x + int(w * 0.10):x + int(w * 0.32)]
    if patch.size == 0:
        return 1.0
    g = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY).astype(np.float32)
    sigma = (g - cv2.GaussianBlur(g, (5, 5), 0)).std()
    return float(np.clip(sigma, 0.3, 2.0))


def main():
    dst_p, src_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
    extra = 1.0
    dy = 0
    if "--scale" in sys.argv:
        extra = float(sys.argv[sys.argv.index("--scale") + 1])
    if "--dy" in sys.argv:
        dy = int(sys.argv[sys.argv.index("--dy") + 1])

    dst = cv2.imread(dst_p)
    src = cv2.imread(src_p)
    dg = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    sg = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    dbox = detect_face(dg)
    sbox = detect_face(sg)
    deyes = detect_eyes(dg, dbox)
    seyes = detect_eyes(sg, sbox)
    print(f"dest face  {tuple(int(v) for v in dbox)}  eyes {[(int(a),int(b)) for a,b in deyes]}")
    print(f"src  face  {tuple(int(v) for v in sbox)}  eyes {[(int(a),int(b)) for a,b in seyes]}")

    if dy:
        deyes = tuple((a, b + dy) for a, b in deyes)

    M = similarity(seyes, deyes, extra)
    warped = cv2.warpAffine(src, M, (dst.shape[1], dst.shape[0]),
                            flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)

    # destination face box, nudged by the same offset
    box = (dbox[0], dbox[1] + dy, dbox[2], dbox[3])
    grow = float(sys.argv[sys.argv.index("--grow") + 1]) if "--grow" in sys.argv else 1.0
    mask, centre = face_mask(dst.shape, box, grow=grow)

    warped = colour_match(warped, dst, mask)

    mode = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else "alpha"
    if mode == "poisson":
        blended = cv2.seamlessClone(warped, dst, mask, centre, cv2.NORMAL_CLONE)
    else:
        # Alpha composite keeps the real face at full strength in the core and
        # only cross-fades at the rim, so identity survives the blend.
        a = (mask.astype(np.float32) / 255.0)[:, :, None]
        blended = np.clip(warped.astype(np.float32) * a +
                          dst.astype(np.float32) * (1 - a), 0, 255).astype(np.uint8)
        # soften just the boundary ring so no hard edge survives
        ring = cv2.absdiff(mask, cv2.erode(mask, np.ones((5, 5), np.uint8)))
        ring = cv2.GaussianBlur(ring, (9, 9), 0)
        soft = cv2.GaussianBlur(blended, (5, 5), 0)
        r = (ring.astype(np.float32) / 255.0)[:, :, None]
        blended = np.clip(blended * (1 - r) + soft * r, 0, 255).astype(np.uint8)

    # re-grain the pasted ellipse so it carries the plate's noise
    sigma = grain_of(dst, dbox)
    noise = np.random.default_rng(7).normal(0, sigma, blended.shape[:2]).astype(np.float32)
    a = (mask.astype(np.float32) / 255.0)[:, :, None]
    blended = np.clip(blended.astype(np.float32) + noise[:, :, None] * a, 0, 255).astype(np.uint8)

    cv2.imwrite(out_p, blended)
    print(f"wrote {out_p}  grain_sigma={sigma:.2f}  eye_scale={extra}")


if __name__ == "__main__":
    main()
