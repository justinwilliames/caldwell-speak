#!/usr/bin/env python3
"""Write generated-images/cast-manifest.json — the record of what produced each asset.

`gemini-3-pro-image` takes no seed, so a render cannot be reproduced bit-for-bit.
The manifest is therefore the accountability mechanism instead: it records, per
character, the archival master's hash and true format, the derived asset's hash,
the generator and model, and the SHA of the prompt block that produced it. If an
asset changes without the manifest changing, something happened off the record.

  python3 scripts/cast-manifest.py [version]
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = sys.argv[1] if len(sys.argv) > 1 else "v8"
G = os.path.join(ROOT, "generated-images")
ARCHIVE = os.path.join(G, "masters-archive")
GEN = os.path.join(ROOT, "scripts", "cast-generate.py")
CAST = ["pulsar", "voyager", "sentinel", "nova", "nebula",
        "echo", "atlas", "iris", "meridian", "vector"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmt(path):
    d = open(path, "rb").read(8)
    if d[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    return "jpeg" if d[:2] == b"\xff\xd8" else "unknown"


def prompt_block(name):
    """The per-character brief inside cast-generate.py, hashed so a silent edit shows."""
    src = open(GEN).read()
    m = re.search(r'\(\s*"%s"\s*,\s*"#[0-9A-Fa-f]{6}"\s*,\s*"""(.*?)"""' % name, src, re.S)
    return hashlib.sha256(m.group(1).encode()).hexdigest()[:16] if m else None


def git(*args):
    try:
        return subprocess.run(["git", "-C", ROOT, *args], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return None


entries = {}
for n in CAST:
    master = None
    for ext in ("jpg", "png"):
        p = os.path.join(ARCHIVE, f"{n}-android-{VER}-master.{ext}")
        if os.path.exists(p):
            master = p
            break
    derived = os.path.join(G, f"{n}-android-{VER}-aligned.png")
    e = {"generator": "google/gemini-3-pro-image", "seeded": False,
         "prompt_sha256_16": prompt_block(n)}
    if master:
        d = open(master, "rb").read()
        e["archival_master"] = {
            "path": os.path.relpath(master, ROOT), "format": fmt(master),
            "sha256": sha(master), "bytes": len(d),
            "c2pa": b"c2pa" in d, "synthid": b"SynthID" in d,
            "iptc_digitalSourceType": b"trainedAlgorithmicMedia" in d,
        }
    else:
        e["archival_master"] = None
    if os.path.exists(derived):
        d = open(derived, "rb").read()
        e["derived"] = {
            "path": os.path.relpath(derived, ROOT), "format": fmt(derived),
            "sha256": sha(derived), "bytes": len(d),
            "declares_provenance": b"trainedAlgorithmicMedia" in d,
        }
    else:
        e["derived"] = None
    entries[n] = e

manifest = {
    "cast_version": VER,
    "generator": "google/gemini-3-pro-image",
    "reproducible": False,
    "reproducibility_note": (
        "gemini-3-pro-image accepts no seed. Re-running a prompt yields a different "
        "face. The archival masters are the authoritative assets; the prompts in "
        "scripts/cast-generate.py are the reproducible part of the record."
    ),
    "pipeline": [
        "scripts/cast-generate.py   -> generated-images/<drone>-android-<ver>.png (JPEG bytes)",
        "scripts/cast-provenance.py -> masters-archive/ + provenance metadata on derived PNGs",
        "scripts/cast-align.py      -> <drone>-android-<ver>-aligned.png (iris-registered)",
        "scripts/cast-gate.py       -> enforces the cast laws, exits non-zero on failure",
    ],
    "git_commit": git("rev-parse", "HEAD"),
    "git_dirty": bool(git("status", "--porcelain")),
    "characters": entries,
}

out = os.path.join(G, "cast-manifest.json")
with open(out, "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")

have_master = sum(1 for e in entries.values() if e["archival_master"])
signed = sum(1 for e in entries.values()
             if e["archival_master"] and e["archival_master"]["c2pa"])
declared = sum(1 for e in entries.values()
               if e["derived"] and e["derived"]["declares_provenance"])
prompts = sum(1 for e in entries.values() if e["prompt_sha256_16"])
print(f"wrote {os.path.relpath(out, ROOT)}")
print(f"  archival masters present        {have_master}/{len(CAST)}")
print(f"  masters with signed credential  {signed}/{len(CAST)}")
print(f"  derived assets declaring AI     {declared}/{len(CAST)}")
print(f"  prompt blocks hashed            {prompts}/{len(CAST)}")
