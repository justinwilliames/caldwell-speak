"""BRIEF DRIFT — is this character still being told to obey a law that was repealed?

Pulsar's lens: the unsaid assumption in the loop itself.

cast-build.py's inject() is deliberately additive — "A correction, once earned,
stays" — because replacing the block each round made defects oscillate. That is the
right call for a rule that is still in force. It is silently wrong for a rule that
is not.

The assumption nobody wrote down is that THE LAWS ARE PERMANENT. They are not. The
chest-orb rule reversed on 2026-08-13 (an orb is now allowed and is explicitly
"measured only; an orb is not a failure"), and the background-tint rule reversed with
it (a coloured glow flooding the frame is allowed; only structure fails). The gate
stopped emitting those failures the moment the code changed. The paragraphs those
failures once injected are still sitting in the prompt file, and inject() will never
remove them. Nothing in this pipeline ever reconciles the brief against the gate.

So the gate can go fully green while the generator is still being ordered to suppress
a feature the spec now wants — and it fails silently in the one direction a gate is
blind to: the character simply never grows the thing, so there is nothing to measure.
That is not a hypothetical. On v8, sentinel's brief still carries the full CHEST ORB
FAILURE paragraph ("nothing mounted, set into or glowing on it... no lamp, no port"),
and sentinel's measured orb is 0 while pulsar (4413), iris (3881), voyager (3512),
atlas (2820) and nova (1878) all carry one. One of the nine has been quietly opted
out of an institutional feature by a dead law, and will be again on every re-render.

WHAT THIS MEASURES — the thing, not a proxy. It does not infer staleness from dates,
diff sizes or ordering. It parses cast-gate.py and every module in cast_checks/ with
the AST and collects the literal text of every failure message the gate is still
CAPABLE of emitting, then asks of each correction in cast-build.py: can anything in
this pipeline still produce the failure that injects you? A correction with no live
emitter is orphaned. It then reads this character's own brief and reports how many
orphaned paragraphs are being fed to the model on its behalf.

Comments and docstrings are excluded by construction — the AST only yields the
arguments to fails.append() and the message returned by a plugin's check(). This
matters: cast-gate.py's prose comment "Chest orbs are PERMITTED" would otherwise be
read as evidence that the chest-orb rule is alive, which is the exact inversion.

THRESHOLD PROVENANCE — there is no tuned constant here; the correct count is zero, so
the line sits at the only place it can. Measured on the v8 cast (2026-08-13): of the
ten corrections in cast-build.py, eight have a live emitter in cast-gate.py ("turned",
"tilted", "chin", "eyes dim", "glow", "eyeCy", "IOD", "background has scenery") and
two do not ("chest orb", "background tinted"). Eight of nine characters carry zero
orphaned paragraphs. sentinel carries one. The check reports 0 for eight and 1 for
one, with no parameter in between to get wrong.

Fails loudly, never silently passes: an unreadable script, an unparseable brief or a
character with no block in cast-generate.py are all failures, because in each case the
brief-versus-gate agreement is unproven, which is operationally the same as broken.
"""
import ast
import os
import re

NAME = "brief_drift"

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, "scripts")
BUILD = os.path.join(SCRIPTS, "cast-build.py")
GATE = os.path.join(SCRIPTS, "cast-gate.py")
GENERATE = os.path.join(SCRIPTS, "cast-generate.py")
CHECKS_DIR = os.path.dirname(os.path.abspath(__file__))

_CACHE = {}


def _norm(s):
    """Whitespace-insensitive form, so a re-wrapped paragraph still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _str_parts(node):
    """Literal text of a Constant or f-string, dropping the interpolated slots."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(v.value for v in node.values
                       if isinstance(v, ast.Constant) and isinstance(v.value, str))
    return None


def _gate_failure_literals():
    """Every failure message this pipeline can still emit.

    Built-in gate: the arguments to fails.append(). Plugins: the string returned in
    any return statement inside check(). Comments and docstrings never appear.
    """
    out = set()

    tree = ast.parse(open(GATE).read())
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if (isinstance(f, ast.Attribute) and f.attr == "append"
                and isinstance(f.value, ast.Name) and f.value.id == "fails"):
            for a in n.args:
                s = _str_parts(a)
                if s:
                    out.add(s)

    for fn in sorted(os.listdir(CHECKS_DIR)):
        # Skip this module: reading my own failure text back in as evidence of a
        # live rule is precisely the self-confirming loop that broke registration.
        if not fn.endswith(".py") or fn.startswith("_") or fn == os.path.basename(__file__):
            continue
        try:
            t = ast.parse(open(os.path.join(CHECKS_DIR, fn)).read())
        except SyntaxError:
            continue
        for fd in ast.walk(t):
            if not (isinstance(fd, ast.FunctionDef) and fd.name == "check"):
                continue
            for r in ast.walk(fd):
                # Returned inline...
                if isinstance(r, ast.Return) and r.value is not None:
                    vals = r.value.elts if isinstance(r.value, ast.Tuple) else [r.value]
                    for v in vals:
                        s = _str_parts(v)
                        if s:
                            out.add(s)
                # ...or bound to a local first. legible64 writes
                #   msg = f"converges with {name} at 48px (dE {d:.1f})"
                #   return best_d, ok, msg
                # and returning a Name yielded no literal, so the rule looked
                # repealed and every brief carrying its correction was failed for
                # obeying a live law. Naming your message before returning it is a
                # style choice, not a repeal.
                if isinstance(r, ast.Assign):
                    s = _str_parts(r.value)
                    if s:
                        out.add(s)
    return out


def _corrections():
    """The CORRECTIONS dict from cast-build.py, read as source rather than imported
    (importing cast-build.py would run the whole build)."""
    tree = ast.parse(open(BUILD).read())
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == "CORRECTIONS":
                    d = {}
                    for k, v in zip(n.value.keys, n.value.values):
                        kt, vt = _str_parts(k), _str_parts(v)
                        if kt is not None and vt is not None:
                            d[kt] = vt
                    return d
    raise ValueError("CORRECTIONS not found in cast-build.py")


def _orphans():
    if "orphans" not in _CACHE:
        live = [_norm(x).lower() for x in _gate_failure_literals()]
        _CACHE["orphans"] = {
            k: v for k, v in _corrections().items()
            if not any(_norm(k).lower() in m for m in live)
        }
    return _CACHE["orphans"]


def _brief(drone):
    """This character's block in cast-generate.py, prompt text and all."""
    if "src" not in _CACHE:
        _CACHE["src"] = open(GENERATE).read()
    s = _CACHE["src"]
    m = re.search(r'^\s*\("%s",\s*"' % re.escape(drone), s, re.M)
    if not m:
        return None
    nxt = re.search(r'^\s*\("(?!%s)[a-z]+",\s*"' % re.escape(drone), s[m.end():], re.M)
    return s[m.start(): m.end() + (nxt.start() if nxt else len(s))]


def check(img, path, rgb):
    base = os.path.basename(path)
    if "-android-" not in base:
        return float("nan"), False, "brief_drift: cannot identify the character from the path"
    drone = base.split("-android-")[0]

    for f in (BUILD, GATE, GENERATE):
        if not os.path.exists(f):
            return float("nan"), False, f"brief_drift: {os.path.basename(f)} missing"

    try:
        orphans = _orphans()
    except Exception as e:
        return float("nan"), False, f"brief_drift: could not reconcile brief with gate ({e})"

    blk = _brief(drone)
    if blk is None:
        return float("nan"), False, f"brief_drift: no brief block for {drone} in cast-generate.py"
    body = _norm(blk).lower()

    stale = [k for k, v in orphans.items() if _norm(v).lower() in body]
    n = len(stale)
    if n:
        return n, False, (f"brief carries {n} repealed rule"
                          f"{'s' if n > 1 else ''}: {', '.join(sorted(stale))}")
    return 0, True, ""
