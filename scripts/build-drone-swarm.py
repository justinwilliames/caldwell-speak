#!/usr/bin/env python3
"""Rebuild assets/readme/drone-swarm.png — the README's "Meet the swarm" lineup.

Composites the full cast (Pulsar + every drone) from their master portraits into
colour-ringed rounded tiles with name + role labels, on the 3x3 grid the README
actually ships. Run it after ANY cast change (new drone, recoloured drone, new
master art):

    python3 scripts/build-drone-swarm.py

Colours and roles are PARSED OUT OF Sources/Models/DroneRegistry.swift, not
copied into a table here. The previous version kept a hand-maintained CAST list
and it drifted exactly as you would expect: it had eight entries with no
Meridian, and a single-row layout that emitted a 1868px-wide strip while the
shipped asset was the 1256x1548 grid — so running it would have silently
regressed the README to an eight-drone lineup. Parsing the registry means a
recolour or a tenth drone cannot desync the art from the code.

Pulsar is not in the registry's drone list (he is the orchestrator, not a drone),
so his row is declared here and his indigo is read from Support/OrbitColors.swift.
"""

import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "macos/Pulsar/Sources/Models/DroneRegistry.swift"
ORBIT_COLORS = REPO / "macos/Pulsar/Sources/Support/OrbitColors.swift"

# Grid geometry, measured off the shipped 1256x1548 asset.
COLS, ROWS = 3, 3
TILE = 354                  # portrait tile edge
RADIUS = 74                 # tile corner radius
BORDER = 4                  # ring width
GAP_EDGE = 47               # left/right/top inset
GAP_X = 50                  # horizontal gutter
ROW_PITCH = 498             # tile-top to tile-top
CANVAS_W = 2 * GAP_EDGE + COLS * TILE + (COLS - 1) * GAP_X      # 1256
CANVAS_H = 1548
BG = (18, 18, 27)           # sampled from the shipped asset
ROLE_GREY = (150, 150, 168)
NAME_DY, ROLE_DY = 30, 79   # label tops, relative to the tile's bottom edge
NAME_PT, ROLE_PT = 44, 32

# Reading order of the shipped asset. Every name here must exist in the registry
# (or be Pulsar); a registry drone missing from this list is a hard error.
ORDER = ["voyager", "sentinel", "nova",
         "nebula", "pulsar", "echo",
         "atlas", "iris", "meridian"]

OUT = REPO / "assets/readme/drone-swarm.png"


def parse_registry():
    """{category: (role, (r,g,b))} straight out of the Swift literals."""
    src = REGISTRY.read_text()
    out = {}
    for cat, role, r, g, b in re.findall(
        r'Drone\(category:\s*"([a-zA-Z0-9_]+)",\s*role:\s*"([^"]*)",\s*'
        r'color:\s*Color\(red:\s*([0-9.]+),\s*green:\s*([0-9.]+),\s*blue:\s*([0-9.]+)\)',
            src):
        out[cat] = (role, tuple(round(float(v) * 255) for v in (r, g, b)))
    out.pop("unknown", None)        # catch-all, not a cast member
    if not out:
        raise SystemExit(f"no Drone(...) entries parsed from {REGISTRY}")
    return out


def parse_pulsar_colour():
    """Pulsar's indigo = OrbitColors.orbitLight, the on-dark accent (#818CF8)."""
    m = re.search(r"`#([0-9A-Fa-f]{6})`[^`]*?static let orbitLight",
                  ORBIT_COLORS.read_text(), re.S)
    if not m:
        raise SystemExit(f"orbitLight hex not found in {ORBIT_COLORS}")
    h = m.group(1)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def build_cast():
    reg = parse_registry()
    cast = []
    for cat in ORDER:
        if cat == "pulsar":
            master, role, colour = REPO / "assets/readme/pulsar.png", "Orchestrator", parse_pulsar_colour()
        else:
            if cat not in reg:
                raise SystemExit(f"{cat} is in ORDER but not in DroneRegistry.swift")
            role, colour = reg[cat]
            role = role.capitalize()
            master = REPO / f"design/drones/{cat}.png"
        if not master.is_file():
            raise SystemExit(f"missing master portrait: {master}")
        cast.append((cat.capitalize(), role, colour, master))
    missing = sorted(set(reg) - set(ORDER))
    if missing:
        raise SystemExit(f"DroneRegistry has drones absent from this layout: {missing}")
    if len(cast) != COLS * ROWS:
        raise SystemExit(f"cast is {len(cast)}, grid holds {COLS * ROWS}")
    return cast


def font(size: int, bold: bool = False):
    for path, idx in [
        ("/System/Library/Fonts/HelveticaNeue.ttc", 1 if bold else 0),
        ("/System/Library/Fonts/Helvetica.ttc", 1 if bold else 0),
    ]:
        try:
            return ImageFont.truetype(path, size, index=idx)
        except Exception:
            continue
    return ImageFont.load_default()


def rounded_tile(master: Path, colour) -> Image.Image:
    """Master portrait resized into a rounded square with a coloured ring."""
    img = Image.open(master).convert("RGB").resize((TILE, TILE), Image.LANCZOS)
    tile = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    mask = Image.new("L", (TILE, TILE), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, TILE - 1, TILE - 1], RADIUS, fill=255)
    tile.paste(img, (0, 0), mask)
    ImageDraw.Draw(tile).rounded_rectangle(
        [0, 0, TILE - 1, TILE - 1], RADIUS, outline=colour + (255,), width=BORDER)
    return tile


def main():
    cast = build_cast()
    im = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(im)
    name_f, role_f = font(NAME_PT, bold=True), font(ROLE_PT)

    for i, (name, role, colour, master) in enumerate(cast):
        col, row = i % COLS, i // COLS
        x = GAP_EDGE + col * (TILE + GAP_X)
        y = GAP_EDGE + row * ROW_PITCH
        tile = rounded_tile(master, colour)
        im.paste(tile, (x, y), tile)
        cx = x + TILE // 2
        for text, f, fill, dy in ((name, name_f, colour, NAME_DY),
                                  (role, role_f, ROLE_GREY, ROLE_DY)):
            w = draw.textlength(text, font=f)
            draw.text((cx - w / 2, y + TILE + dy), text, fill=fill, font=f)

    im.save(OUT)
    print(f"wrote {OUT} ({im.size[0]}x{im.size[1]}, {len(cast)} tiles, "
          f"{COLS}x{ROWS} grid)")
    for name, role, colour, master in cast:
        print(f"  {name:<9} {role:<13} rgb{colour}  {master.relative_to(REPO)}")


if __name__ == "__main__":
    main()
