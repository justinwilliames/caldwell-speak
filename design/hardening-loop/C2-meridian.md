# C2 — Meridian (Auditor + Legal/Distribution)

**Verdict: all five cycle-1 fixes are real — none papered over. Two carry incomplete coverage (one
landed with no regression test, one revert path covers 2 of 6 hooks), one C1 finding was WRONG, and
my audit surface was contaminated mid-flight by a concurrent agent's uncommitted edits.
Legal/distribution surface is clean.**

## EVIDENCE HAZARD

Tree was **not** clean: ` M AudioQueueActor.swift`, ` M DaemonAuth.swift`, `?? C2-atlas.md` — a
parallel drone landing C1 #4/#5/#6/#7 uncommitted (156 insertions). So my **59 passed, 0 failed**
measures the *dirty* tree, not 35aa74c, and the rotation code below is in no commit. Claim 1 I
re-verified against the commit itself. Per `[[parallel-sessions-git-worktree-isolation]]`,
concurrent actors on one tree make every audit non-reproducible.

## PART A — cycle-1 claim audit

| Claim | Verdict | Evidence |
|---|---|---|
| 1. `resumeAfterUnmute` re-stamps | **VERIFIED fix / INCOMPLETE cover** | Stamp committed, `AudioQueueActor.swift:858`. Every re-arm site checked: `:721` purges *before* `insert` (`:711` vs `:719`) so the fresh `enqueuedAt` survives, and purging aged *held* lines there is `muteNow`'s intent (`:837-840`); `:1052` follows the `:1042` stamp; `:956` clears the flag only. **No un-stamped re-arm remains.** But 35aa74c touches **no test file** — `DroneLifecycleTests.swift:247` asserts the *hold*, never the resume. |
| 2. CI `--break-system-packages` | **VERIFIED** | `gh run view 30517256340` (35aa74c): all steps ✓ incl. `✓ Install Pillow` **and `✓ Cast-consistency check`** — gate reachable and run. Caveats: `gh` defaults to `upstream` (`tomc98/speak`), returning `[]`; `build.yml` + `package-dmg.yml` **share `name: Build Pulsar`**, hence the pass/fail *pair* per commit. |
| 3. `PulsarConfig.set` locking | **VERIFIED** | Whole read-modify-write inside `writeLock` (`:181-186`). `reload()` outside is safe: `loadCoerced()` (`:150-161`) takes no lock, so `writeLock` never nests `lock`; `reload()` (`:164-167`) takes `lock` only — no deadlock, no lost update. **Papered-over comment:** `:273-276` claims migration persists "through `set()`"; `:277-278` does a raw unlocked `data.write`. |
| 4. `install-hooks.sh` realpath | **VERIFIED dedup / INCOMPLETE revert** | Both orders on temp settings: **6 hooks** each way, zero dupes. Uninstall from the *opposite* path removed **both spellings** (`uninstall-hooks.sh:57-63`). **But install wires 6, uninstall removes 2** — `Stop`/`chime.sh`, `SessionStart`, `UserPromptSubmit` survive by design (`:8-11`), so Voyager's dupes aren't tool-removable. Latent: `_canon` realpaths only the first token, so `python3 a.py`/`b.py` false-dedup. |
| 5. `say.sh` 401 warning | **VERIFIED** | `say.sh:22-24` fires only when token empty **and** `/health` succeeds — daemon down ⇒ silent. Twins byte-identical (`diff -q`). |

**C1 finding that was WRONG:** Sentinel #7, "`speech.jsonl` grows without bound". Rotation exists
(5 MB, two generations, `DaemonAuth.swift:81/242/284`) — uncommitted, so C1 was right at review time
and the claim is closing. Live: 26,806 bytes / 113 records, `-rw-------`.

## PART B — legal & distribution

- **Notices accurate.** All **25** `Package.resolved` pins present, versions matching (scripted).
  `Package.resolved` untouched since `30b03e0`, notices regenerated after. No new dependency today.
- **Pillow creates no obligation.** CI-only tool for `cast-check.sh` — absent from
  `Package.resolved` and from the bundle (`find /Applications/Pulsar.app -iname "*NOTICE*"` returns
  only our own file). Not distributed, so nothing to disclose.
- **Notices reach the bundle in BOTH paths** — `build-pulsar-app.sh:91`, `package-dmg.yml:122`.
  Live file 59,529 bytes, `diff -q` vs repo → **IDENTICAL**. Bundle 0.9.18.1, min-OS 26.0.
- **PRIVACY.md — one fix.** **Sparkle sentence accurate**: `Info.plist` has only `SUFeedURL` +
  `SUPublicEDKey`, no `SUEnableAutomaticChecks`, so Sparkle 2.x does prompt on first launch.
  "Append-only" stays true (rotation renames), but name `speech.jsonl.1` once it lands. **Its own
  verify recipe misfires:** `grep -r "https://" macos/Pulsar/Sources` returns **4 hits**
  (`AboutView.swift:5-7`, `PopoverRootView.swift:131` — user-clicked `Link`s). The claim holds; the
  instruction invites a check that appears to falsify it. Scope it to `Sources/Engine Sources/HTTPServer`.
- **Disclaimer strong in docs, absent from the product.** `README.md:53` and
  `pulsar-team/SKILL.md:34` are excellent (the latter bars attributed quotes). But
  `grep -rni "fictional|not a real person" macos/Pulsar/Sources/Views/` returns **nothing** — the
  shipped app renders nine named characters with faces and voices, no notice. `AboutView.swift` is
  the home; `docs/PRIVACY.md` is silent too.
- **§1 names clean.** No third-party person, no fabricated employer. `References:` lines cite public
  material (Apple docs, Stripe Press, Linear, Braze) — citations, not employment claims, so the
  disclaimer over-covers: the safe direction. "Justin" appears 13× (incl. §1:37), the author
  attributing governance in his own public MIT repo. Benign.

## The single thing I'd fix next

**Add the regression test for the unmute resume** — the only cycle-1 fix with no automated guard,
protecting the day's headline feature from being silently undone, which already happened once. The
seam exists: `_test_ageDrainProgress(seconds:)` (`:635`) + `_test_queueDepth()`. Beside
`DroneLifecycleTests.swift:247`: hold 3, age drain past 60s, `resumeAfterUnmute()`, assert depth
still 3. Everything else here is a comment or a second-order hazard; this one is behaviour.
