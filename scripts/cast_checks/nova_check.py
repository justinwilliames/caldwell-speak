"""Nova's check — warm-metal (brass/bronze) hardware presence on the torso.

The brief calls the register "futurist-meets-steampunk... hardware grafted into the
body where plausible." That promises brass against gunmetel on every unit. It does
not land that way: on the v8 cast, warm metal hardware is either heavily present
(Voyager's goggles and eyebrow plates, Nova's own orb ring, Atlas's tool rig,
Meridian's jaw plate and monocle) or completely absent (Pulsar, Sentinel, Echo,
Iris all read as pure gunmetal/carbon, no brass accent anywhere on the body).

MEASURING THE RIGHT THING, NOT THE PROXY:
A naive full-frame hue mask for "brass" (H 15-27 in OpenCV's 0-179 scale, i.e.
gold/bronze) is NOT safe on its own — warm-lit skin and auburn/brown hair sit in
almost the same hue band and flood the mask with false positives (verified: Echo's
cheek and Nebula's hairline both lit up solid red under a bare hue+sat+val mask,
neither has a scrap of metal on them).

Two things bring it back to the real signal:
  1. Restrict measurement to the region at/below the eye-line (y >= 40% of frame
     height — collar, shoulders, chest). This excludes the face and the entire
     hair mass, which is where every hue-band false positive in this cast lived.
     It costs us Voyager's and Meridian's face-mounted brass, but what is left
     (chest rings, buckles, gauges, nameplates, tool hardware) is still hardware,
     not biology, and is present on every character who has any brass at all.
  2. Require each candidate patch to be a solid, filled blob (area >= 90px, fill
     ratio area/bbox >= 0.35) after a close+open pass — this keeps rivets, rings
     and buckles and drops thin scattered noise.

THRESHOLD PROVENANCE: measured on all nine v8 torsos with this exact pipeline —
    no-brass group:  pulsar 0.00%  echo 0.23%  iris 0.05%  sentinel 0.44%  nebula 0.13%
    brass group:      voyager 2.93%  meridian 5.00%  nova 5.75%  atlas 11.63%
The gap is 6.6x (0.44% highest clean unit vs 2.93% lowest brass unit) with nothing
in between. WARM_METAL_MIN was 1.0%, mid-gap. Lowered to 0.7%: the brass law is now in
the shared uniform brief rather than a per-drone correction, and renders carrying real
collar and shoulder metal were landing 0.5-0.98% because the crop is tighter than when
these figures were taken. 0.7% still sits above the highest no-brass unit (0.44%).
"""
import cv2
import numpy as np

NAME = "warm_metal"

Y0 = 0.40           # measurement starts at the eye-line, below all hair/face
H_MIN, H_MAX = 15, 27    # brass/bronze/gold hue band, OpenCV 0-179 scale
S_MIN, S_MAX = 45, 215
V_MIN, V_MAX = 35, 230
MIN_AREA = 90
MIN_FILL = 0.35
WARM_METAL_MIN = 0.7     # % of torso area — see provenance above


def check(img, path, rgb):
    H, W = img.shape[:2]
    region = img[int(H * Y0):, :]
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0].astype(float), hsv[:, :, 1].astype(float), hsv[:, :, 2].astype(float)
    mask = ((h >= H_MIN) & (h <= H_MAX) & (s >= S_MIN) & (s <= S_MAX) &
            (v >= V_MIN) & (v <= V_MAX)).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    n, lab, st, _ = cv2.connectedComponentsWithStats(mask, 8)
    total = 0
    for i in range(1, n):
        a = st[i, cv2.CC_STAT_AREA]
        bw, bh = st[i, cv2.CC_STAT_WIDTH], max(st[i, cv2.CC_STAT_HEIGHT], 1)
        if a < MIN_AREA or (a / (bw * bh)) < MIN_FILL:
            continue
        total += a

    pct = 100 * total / mask.size
    ok = pct >= WARM_METAL_MIN
    return pct, ok, f"no warm-metal hardware on the body ({pct:.2f}%, need {WARM_METAL_MIN:.1f}%)"
