# Team-authored gate checks

The Pulsar team writes gates here. Any `*.py` in this directory exposing `NAME` and
`check()` is loaded by `scripts/cast-gate.py` and run against all nine characters.

```python
NAME = "short_key"            # column name in the gate table

def check(img, path, rgb):
    """img: BGR numpy array of the aligned portrait
       path: file path (for landmark work via cast_pose)
       rgb: the character's locked brand colour, 0..1 floats
       returns (value, ok, message)"""
    return value, ok, f"what failed ({value:.0f})"
```

Rules for a check to be worth adding:

1. **It must discriminate.** Show it passing a character that is fine and failing one
   that is not. A check that fails everything or nothing is noise.
2. **Measure the thing, not a proxy.** This gate has three times measured something
   adjacent to the real property and reported confidently — self-confirming
   registration, shoulder piping counted as a chest core, and head pose inferred from
   glowing blobs. Prefer landmarks and direct measurement.
3. **State the threshold's provenance** in a comment: what you measured on the current
   cast, and why the line sits where it does.
4. **Fail loudly, never silently pass.** If the measurement cannot be made, that is a
   failure, not a pass.
