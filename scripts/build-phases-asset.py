#!/usr/bin/env python3
"""Pulsar development phases -> LinkedIn portrait asset (1200x1500).

Three bands, real art from each era:
  1. May 2026  - Caldwell, the single agent (extracted from git 1f5556b)
  2. Jul 2026  - the six original drones (v0.9.0, commit 4ecae94)
  3. Now       - the nine-drone cast (Rev 9 masters)

Branding: Orbit "ink" theme (near-black field, indigo accent), Bricolage
Grotesque + Inter, and the Orbit app icon. Icon only, never the wordmark.
Job titles come from pulsar-team/SKILL.md personas and DroneRegistry.swift.

Text is composited here with PIL, never baked into an AI render.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

SP = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.expanduser("~/code/pulsar")
BRAND = os.path.expanduser("~/code/get-orbit/public/images")
FONTS = os.path.expanduser("~/.claude/skills/linkedin-post-writer/assets/fonts")

W, H = 1200, 1500

# ---- Orbit "ink" theme (banner-style.md): product/tech posts --------------
BG = (10, 10, 11)            # #0A0A0B  near-black field
PANEL = (18, 18, 21)         # subtle band wash
RULE = (38, 38, 44)
INK = (245, 245, 247)
MUTE = (150, 150, 162)
INDIGO = (129, 140, 248)     # #818CF8  Orbit ink accent

COLOURS = {
    "voyager": (242, 168, 59), "sentinel": (107, 184, 235), "nova": (92, 209, 107),
    "nebula": (232, 92, 209), "echo": (46, 191, 184), "atlas": (128, 64, 191),
    "iris": (242, 97, 120), "meridian": (60, 96, 150), "pulsar": (129, 140, 248),
    "caldwell": (176, 156, 122),
}

# Job titles, not task descriptions. Sourced from pulsar-team/SKILL.md §1.x
# persona headings, reconciled with the DroneRegistry `role` field.
TITLES = {
    "caldwell": "Assistant",
    "pulsar": "Chief of Staff",
    "voyager": "Data Engineer",
    "sentinel": "Data Analyst & QA",
    "nova": "Software Engineer",
    "nebula": "Creative Director",
    "echo": "Technical Writer",
    "atlas": "Generalist",
    "iris": "Head of Marketing",
    "meridian": "General Counsel",
}

DISPLAY = f"{FONTS}/Bricolage.ttf"
BODY = f"{FONTS}/Inter.ttf"


def font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    if weight:
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
    return f


F_TITLE = font(DISPLAY, 62, "ExtraBold")
F_SUB = font(BODY, 25, "Regular")
F_PHASE = font(DISPLAY, 36, "Bold")
F_META = font(BODY, 21, "Regular")
F_EYEBROW = font(BODY, 18, "Bold")
F_NAME = font(BODY, 19, "Bold")
F_ROLE = font(BODY, 16, "Regular")


def squircle_mask(size, radius_frac=0.28):
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, size * 4 - 1, size * 4 - 1], radius=int(size * 4 * radius_frac), fill=255)
    return m.resize((size, size), Image.LANCZOS)


def chip(path, size, ring):
    """Square-crop -> squircle -> coloured ring + soft outer glow."""
    im = Image.open(path).convert("RGB")
    s = min(im.size)
    im = im.crop(((im.width - s) // 2, (im.height - s) // 2,
                  (im.width - s) // 2 + s, (im.height - s) // 2 + s))
    im = im.resize((size, size), Image.LANCZOS)

    mask = squircle_mask(size)
    pad = int(size * 0.22)
    canvas = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))

    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gd = Image.new("L", canvas.size, 0)
    gd.paste(mask, (pad, pad))
    glow.paste(ring + (150,), (0, 0), gd)
    glow = glow.filter(ImageFilter.GaussianBlur(pad * 0.55))
    canvas.alpha_composite(glow)

    art = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    art.paste(im, (0, 0), mask)
    canvas.alpha_composite(art, (pad, pad))

    ov = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(
        [2, 2, size * 4 - 3, size * 4 - 3], radius=int(size * 4 * 0.28),
        outline=ring + (255,), width=10)
    canvas.alpha_composite(ov.resize((size, size), Image.LANCZOS), (pad, pad))
    return canvas, pad


def row(canvas, paths, names, y, size, gap, cx=None, label=True, titles=False):
    """Lay out a row of chips.

    `titles` adds the job-title line under the name. Title text must stay
    inside its own chip+gap column so neighbouring labels never collide; the
    assertion below fails the build rather than shipping overlapping type.
    """
    total = len(paths) * size + (len(paths) - 1) * gap
    x = (W - total) // 2 if cx is None else cx
    d = ImageDraw.Draw(canvas)
    for p, n in zip(paths, names):
        c, pad = chip(p, size, COLOURS[n])
        canvas.alpha_composite(c, (x - pad, y - pad))
        if label:
            lab = n.upper()
            tw = d.textlength(lab, font=F_NAME)
            d.text((x + (size - tw) / 2, y + size + 13), lab,
                   font=F_NAME, fill=INK)
            if titles:
                t = TITLES[n]
                tww = d.textlength(t, font=F_ROLE)
                assert tww <= size + gap, \
                    f"title '{t}' ({tww:.0f}px) overflows column {size + gap}px"
                d.text((x + (size - tww) / 2, y + size + 40), t,
                       font=F_ROLE, fill=MUTE)
        x += size + gap
    return y + size + (66 if titles else 34 if label else 0)


def band_label(d, y, eyebrow, phase, meta):
    d.text((70, y), eyebrow, font=F_EYEBROW, fill=INDIGO)
    d.text((70, y + 28), phase, font=F_PHASE, fill=INK)
    d.text((70, y + 76), meta, font=F_META, fill=MUTE)


img = Image.new("RGBA", (W, H), BG + (255,))
d = ImageDraw.Draw(img)

# ---- header: Orbit app icon + Pulsar wordless lockup --------------------
logo = Image.open(f"{BRAND}/orbit-app-icon.png").convert("RGBA")
LS = 76
logo = logo.resize((LS, LS), Image.LANCZOS)
glow = Image.new("RGBA", (LS + 60, LS + 60), (0, 0, 0, 0))
glow.paste(INDIGO + (110,), (30, 30), logo.split()[3])
img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)), (70 - 30, 66 - 30))
img.alpha_composite(logo, (70, 66))

d.text((166, 62), "PULSAR", font=F_TITLE, fill=INK)
d.text((168, 136), "One agent became nine.", font=F_SUB, fill=MUTE)
d.line([(70, 196), (W - 70, 196)], fill=RULE, width=2)

# ---- band 1: Caldwell (label left, portrait inline right) ---------------
band_label(d, 228, "MAY 2026", "One agent",
           "Caldwell. A single voice for every job.")
row(img, [f"{SP}/caldwell.png"], ["caldwell"], 218, 132, 0, cx=950, titles=True)

d.line([(70, 432), (W - 70, 432)], fill=RULE, width=2)

# ---- band 2: the original six (names only, titles live in band 3) ------
band_label(d, 456, "JULY 2026", "Six drones",
           "The swarm. A named specialist per lens.")
p2 = ["voyager", "sentinel", "nova", "nebula", "echo", "atlas"]
row(img, [f"{SP}/p2/{n}.png" for n in p2], p2, 572, 136, 22)

d.line([(70, 772), (W - 70, 772)], fill=RULE, width=2)

# ---- band 3: the nine (hero, two rows of 5 + 4, with job titles) --------
band_label(d, 804, "NOW", "Nine specialists",
           "Marketing and legal joined the team.")
p3 = ["pulsar", "voyager", "sentinel", "nova", "nebula",
      "echo", "atlas", "iris", "meridian"]


def p3path(n):
    return (f"{REPO}/assets/readme/pulsar.png" if n == "pulsar"
            else f"{REPO}/design/drones/{n}.png")


ra, rb = p3[:5], p3[5:]
row(img, [p3path(n) for n in ra], ra, 918, 136, 34, titles=True)
row(img, [p3path(n) for n in rb], rb, 1136, 136, 34, titles=True)

d.text((70, 1382), "Built on Speak by Thomas Csere.  Open source, MIT.",
       font=F_META, fill=MUTE)
d.text((70, 1418), "get.yourorbit.team/pulsar", font=F_META, fill=INDIGO)

out = f"{SP}/pulsar-phases.png"
img.convert("RGB").save(out, "PNG", optimize=True)
print("WROTE", out, Image.open(out).size)
