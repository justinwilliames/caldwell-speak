#!/usr/bin/env python3
"""Remove accumulated corrections from the briefs — SAFELY.

WHY THIS EXISTS. Stripping stale correction text with a file-wide regex has now
destroyed brief blocks twice. The failure is always the same shape: a pattern
like

    re.sub(r'\\n*LIGHTING FAILURE[^\\n]*(?:\\n(?!\\n)[^\\n]*)*\\n', '\\n', src)

runs off the end of the paragraph it meant to remove, because the very next
non-blank lines are `=== END CORRECTION ===` and then the block's own closing
`\"\"\"),`. Eating those merges two characters into one and, on the last entry,
deletes a whole drone. The first time it removed Voyager and Sentinel; the second
it removed Vector outright and left Pulsar unterminated, and the build died with
`ValueError: substring not found` several minutes later — far from the cause.

THE RULE, which the forge states and which this script enforces: cut on EXPLICIT
BOUNDARIES, never on "the next thing that looks like the end". Every edit here is
bounded by the character's own start marker and the next character's start
marker, both located by an anchored pattern; the closing delimiter is re-asserted
rather than assumed; and nothing is written unless the result still parses.

  python3 scripts/cast-strip-corrections.py            # strip every drone
  python3 scripts/cast-strip-corrections.py nova iris  # strip named drones
  python3 scripts/cast-strip-corrections.py --check    # report, change nothing
"""
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "scripts", "cast-generate.py")
CAST = ["pulsar", "voyager", "sentinel", "nova", "nebula",
        "echo", "atlas", "iris", "meridian", "vector"]

OPEN = '"""'
CLOSE = '"""),'
BEGIN = "=== AUTOMATED CORRECTION ==="
END = "=== END CORRECTION ==="


def spans(src):
    """(name, body_start, body_end) for each brief, on explicit boundaries only."""
    marks = []
    for n in CAST:
        m = re.search(r'^\s*\("%s",\s*"#[0-9A-Fa-f]{6}",\s*%s' % (n, re.escape(OPEN)),
                      src, re.M)
        if m:
            marks.append((n, m.start(), m.end()))
    marks.sort(key=lambda t: t[1])
    if not marks:
        sys.exit("no brief blocks found — refusing to touch the file")
    tail = src.index("\n]\n", marks[-1][1])
    out = []
    for i, (n, _, body_start) in enumerate(marks):
        body_end = marks[i + 1][1] if i + 1 < len(marks) else tail
        out.append((n, body_start, body_end))
    return out


def strip(body):
    """Drop the correction section and re-assert the closing delimiter."""
    i = body.find(BEGIN)
    kept = body[:i] if i >= 0 else body
    # The delimiter is rebuilt, never inherited: if a previous bad edit ate it,
    # this is where it comes back rather than where the file silently breaks.
    kept = kept.split(CLOSE)[0].rstrip()
    return kept + "\n" + CLOSE + "\n\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv
    targets = args or CAST
    src = open(GEN).read()

    report, pieces, prev = [], [], 0
    for name, body_start, body_end in spans(src):
        body = src[body_start:body_end]
        pieces.append(src[prev:body_start])
        if name in targets:
            has = BEGIN in body
            missing_close = CLOSE not in body
            new = strip(body)
            if has or missing_close:
                report.append((name, len(body) - len(new), has, missing_close))
            pieces.append(new)
        else:
            pieces.append(body)
        prev = body_end
    pieces.append(src[prev:])
    out = "".join(pieces)

    try:
        ast.parse(out)
    except SyntaxError as e:
        sys.exit(f"refusing to write: result does not parse ({e})")
    if len(spans(out)) != len(spans(src)):
        sys.exit("refusing to write: a brief block would be lost")

    for name, saved, had, broken in report:
        note = "corrections removed" if had else ""
        if broken:
            note = (note + "; " if note else "") + "REPAIRED missing closing delimiter"
        print(f"{name:10} {saved:>6} chars   {note}")
    if not report:
        print("nothing to strip — every brief is already clean")
    if check_only:
        print("\n--check: nothing written")
        return
    open(GEN, "w").write(out)
    print(f"\nwrote {os.path.relpath(GEN, ROOT)} — {len(spans(out))} briefs intact, parses clean")


if __name__ == "__main__":
    main()
