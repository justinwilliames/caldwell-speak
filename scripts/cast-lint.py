#!/usr/bin/env python3
"""Lint the cast SPEC — every drone held to the same standard.

The image gate checks renders. This checks the briefs behind them, because the
quality floor slipped in the spec long before it showed up in a picture: some
characters carried eleven paragraphs of identity and hardware while others carried
three, and roles, colour-carriers and modification sites silently collided.

  python3 scripts/cast-lint.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "scripts", "cast-generate.py")
REG = os.path.join(ROOT, "macos/Pulsar/Sources/Models/DroneRegistry.swift")

# Every character brief must cover all of these. Keyed by label → regex alternatives.
REQUIRED = {
    "identity":    r"FIXED:|FINAL IDENTITY|FEMALE,|MALE,",
    "physique":    r"BUILD:|PHYSIQUE|frame|shoulders|build",
    "face":        r"[Ff]ace shape|FACE AND BEARING|[Ff]ace:|cheekbone|jawline|jaw,|brow|nose",
    "hair":        r"HAIR:|Hair:|hair\b|BALD|bald|buzzcut|shaved",
    "expression":  r"[Ee]xpression",
    "hardware":    r"HARDWARE|PROFESSION HARDWARE|hardware",
    "grooves":     r"GROOVE|groove|seam|panel line",
    "body_mod":    r"BODY MODIFICATION|MODIFICATION|grafted|socketed|plated|implant",
    "lit_elements": r"LIT ELEMENTS|LIT ELEMENT",
    "uniform_tier": r"UNIFORM TIER|EXECUTIVE|FIELD GEAR|WORKING GEAR|tunic|uniform",
}
MIN_WORDS = 160


def briefs():
    src = open(GEN).read()
    out = {}
    for m in re.finditer(r'\(\s*"(\w+)",\s*"(#[0-9A-Fa-f]{6})",\s*"""(.*?)"""\s*\)', src, re.S):
        out[m.group(1)] = (m.group(2), m.group(3))
    return out


def _edit(a, b):
    """Levenshtein — small, and only ever run on single words."""
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def near_duplicate(a, b):
    """True when two job titles differ by a single, near-identical word.

    'Project Manager' and 'Product Manager' are not the same string and read as
    the same job — the pair sat in the cast unnoticed because the check only ever
    tested equality. Differing by one token is not enough on its own ('Marketing
    Manager' is a genuinely different seat); the changed token must also be a
    near-miss spelling of its counterpart.
    """
    ta, tb = a.lower().split(), b.lower().split()
    if len(ta) != len(tb):
        return False
    diff = [(x, y) for x, y in zip(ta, tb) if x != y]
    return len(diff) == 1 and _edit(*diff[0]) <= 2



# --- self-contradiction -----------------------------------------------------
# A brief that mandates a piece of kit and later bans it is the single most
# expensive defect this pipeline produces, because the render obeys whichever
# instruction it weighted last and nobody can tell which one that was. Sentinel
# found two live examples in one review: Nova's brief mandated a grinding shield
# and then twice said NO face shield (so she grew goggles, duplicating Voyager's),
# and Nebula's mandated a colour-calibration loupe and then said "REMOVE THE EYE
# LOUPE ENTIRELY — no eyepiece of any kind", leaving her with no profession
# hardware at all and a LIT ELEMENTS line citing an indicator bead that no longer
# existed. The accumulate-forever correction rule manufactures exactly this, and
# until now nothing read a brief back against itself.
KIT = ["goggle", "visor", "loupe", "shield", "helmet", "mask", "antenna",
       "scope", "monocle", "eyepiece", "magnifier", "headband", "crown plate",
       "cheek plate", "chest orb", "halo", "circlet"]

MANDATE = re.compile(
    r"(?:\bHARDWARE\b|\bwears?\b|\bcarr(?:y|ies|ying)\b|\bhas\b|\bwith\b|"
    r"\bmounted\b|\bsits?\b|\bholding\b|\bgive (?:her|him|them)\b|"
    r"\bpushed\b|\bparked\b|\bclipped\b|\bbuttoned\b|\bworn\b)[^.\n]{0,70}$",
    re.I)

NEGATION = re.compile(
    r"(?:\bNO\b|\bnot\b|\bremove\b|\bwithout\b|\bno longer\b|\bnever\b)[^.\n]{0,70}$",
    re.I)


def contradictions(text):
    """Kit nouns that are both MANDATED somewhere and FORBIDDEN somewhere else.

    A bare mention is not a mandate. Briefs legitimately explain their own history
    ("earlier versions gave her a laboratory inspection visor and it looked
    ridiculous"), and counting that as a requirement made the check cry wolf on
    four nouns in one brief — which is worse than not having it, because a gate
    nobody trusts is a gate nobody reads. So a mention only counts as REQUIRED
    when a mandate verb sits just before it, and only counts as FORBIDDEN when a
    negation sits just before it. Everything else is neutral narration.
    """
    out = []
    for noun in KIT:
        pos = neg = 0
        for m in re.finditer(re.escape(noun), text, re.I):
            lead = text[max(0, m.start() - 70):m.start()]
            if NEGATION.search(lead):
                neg += 1
            elif MANDATE.search(lead):
                pos += 1
        if pos and neg:
            out.append(f"{noun} (mandated {pos}x, forbidden {neg}x)")
    return out


def roles():
    src = open(REG).read()
    found = dict(re.findall(r'category:\s*"(\w+)",\s*role:\s*"([^"]+)"', src))
    # Pulsar carries no DroneRegistry entry — he is the seat, not a spawn target —
    # so his title lives in RosterView. Scanning only the registry checked nine
    # drones while the banner claimed all ten, which is how a Project Manager and
    # a Product Manager came to sit side by side unreported.
    roster = os.path.join(ROOT, "macos/Pulsar/Sources/Views/Popover/RosterView.swift")
    if os.path.exists(roster):
        for cat, role in re.findall(r'CastMember\(id:\s*"(\w+)",[^)]*?role:\s*"([^"]+)"',
                                    open(roster).read()):
            found.setdefault(cat, role)
    return found


B, R = briefs(), roles()
fails = []

print(f'{"drone":10}{"words":>7}{"missing sections":>44}')
for name, (hexc, text) in B.items():
    words = len(text.split())
    missing = [k for k, pat in REQUIRED.items() if not re.search(pat, text, re.I)]
    if words < MIN_WORDS:
        fails.append(f"{name}: brief only {words} words (floor {MIN_WORDS})")
    if missing:
        fails.append(f"{name}: brief missing {', '.join(missing)}")
    print(f'{name:10}{words:>7}{(", ".join(missing) or "-"):>44}')

# distinct role per drone, Pulsar included
print()
seen = {}
for cat, role in R.items():
    if cat in ("unknown",):
        continue
    if role.lower() in seen:
        fails.append(f"role '{role}' shared by {seen[role.lower()]} and {cat}")
    for other, ocat in seen.items():
        if near_duplicate(role, other):
            fails.append(f"roles too close to tell apart: "
                         f"{ocat} '{other.title()}' vs {cat} '{role}'")
    seen[role.lower()] = cat
for _d, (_hex, _t) in B.items():
    _c = contradictions(_t)
    if _c:
        fails.append(f"{_d}: brief contradicts itself on {'; '.join(_c)}")

print(f"distinct roles: {len(seen)} across {len(seen)} drones"
      + ("" if len(fails) == 0 else ""))

# a brief must not still enforce a repealed rule
for name, (_, text) in B.items():
    if re.search(r"THERE IS NO CHEST ORB", text):
        fails.append(f"{name}: brief carries a repealed rule (chest orb)")

# colour-carrier and modification site must be unique — this is what stops
# nine faces converging on one design
def site(text):
    m = re.search(r"BODY MODIFICATION[^\n]*?—\s*([^.\n]{0,60})", text)
    return (m.group(1).strip().lower() if m else None)

sites = {}
for name, (_, text) in B.items():
    s = site(text)
    if not s:
        continue
    for other, prev in sites.items():
        if prev and (prev in s or s in prev):
            fails.append(f"{name} and {other} share a modification site ({s[:40]})")
    sites[name] = s

print()
if fails:
    print("FAIL")
    for f in fails:
        print("  " + f)
else:
    print(f"PASS — {len(B)} briefs, all sections present, all roles and mod sites distinct")
sys.exit(1 if fails else 0)
