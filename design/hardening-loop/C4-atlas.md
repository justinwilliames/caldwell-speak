# Cycle 4 — Atlas (dead-view excision + cycle-3 audit), commit 6b97ab4

**Verdict:** Job A confirmed and executed — three files were genuinely dead,
now deleted. Job B: all five cycle-3 claims VERIFIED, no wrong or incomplete
covers found. One honest craft note on the disclaimer placement, not a defect.
Dry lens overall — nothing new beyond the planned deletion.

## Job A — dead-view deletion

Grepped every reference to all three types (`grep -rn "HistoryPanelView\|
QueuePanelView\|NowPlayingView" . --include="*.swift" --include="*.md"`):
each type appears exactly once — its own `struct X: View` declaration. Zero
constructor calls (`X(`) anywhere. `PopoverRootView.swift:8-20`'s
`DashboardTab` enum has exactly two cases (`roster`, `settings`) — no
Missions/History/Queue/NowPlaying tab exists to host them. The only other hit
was a doc comment in `PortraitView.swift:20` naming `NowPlayingView` as a
caller that "keeps working" — stale prose, not a reference.

Confirmed dead. Deleted:
- `macos/Pulsar/Sources/Views/Popover/HistoryPanelView.swift` (179 lines)
- `macos/Pulsar/Sources/Views/Popover/QueuePanelView.swift` (96 lines)
- `macos/Pulsar/Sources/Views/Popover/NowPlayingView.swift` (72 lines)

Also fixed the now-stale doc comment in `PortraitView.swift:18-20` ("...so
NowPlayingView / FloatingPortraitView keep working" → "...so
FloatingPortraitView keeps working").

Verification:
- `cd macos/Pulsar && swift build -c release` → `Build complete! (12.33s)`
- `./scripts/run-tests.sh` → `Drone lifecycle tests: 70 passed, 0 failed / ALL PASSED ✓`
- `./scripts/cast-check.sh` → `cast-check: PASS`, all 10 checks agree.

## Job B — cycle-3 claim audit

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | package-dmg.yml stages pulsar-team AND hard-fails if missing | **VERIFIED** | `.github/workflows/package-dmg.yml:160-172` — the staging block lives inside the same `run:` step as `id: bundle` (opens `set -e` at line 108), same shell script, no subshell/backgrounding. The guard `test -s "$CI_STAGE/skills/pulsar-team/SKILL.md" \|\| { echo "::error::..."; exit 1; }` is an explicit `exit 1` on failure — it terminates the step regardless of `set -e` (the `\|\|` branch runs unconditionally on test failure and its body exits directly, not swallowed by the `\|\|`). It would catch the exact failure it targets: `cp pulsar-team/SKILL.md` failing silently, or the source dir not existing, both leave the destination empty/absent and the `test -s` fails. |
| 2 | Persona disclaimer above cast, `.secondary` | **VERIFIED** | `RosterView.swift:54` header "MEET THE TEAM", disclaimer text block at `:64-73` sits directly after the header and before `ForEach(cast)` at `:75` — above the fold, no scroll. `.font(.caption)` + `.foregroundStyle(.secondary)` at `:70-71` — not `.tertiary`/`.caption2`. Honest craft take: placement now reads correctly as informational rather than buried, but it is still the literal first thing painted on the default tab, ahead of any cast content — closer to a compliance banner than a cast-list flourish. Not a defect; a legitimate trade-off (legibility over delight) that cycle 3 chose deliberately and got right for its actual job. |
| 3 | speakingOrbitCap = 6, idle untouched | **VERIFIED** | `FloatingHeadsView.swift:86` `static let speakingOrbitCap = 6`. Applied only at `:342` `if speaker != nil, orbitKeys.count > Self.speakingOrbitCap`. When `speaker == nil` (idle) the cap branch never executes, so the nine-slot `symmetricClusterOffsets` path is untouched, matching the C3-nova description. |
| 4 | uninstall-hooks.sh docs match 6-hook behavior | **VERIFIED** | Header (`:1-16`) explicitly lists all 6: SubagentStart, SubagentStop, Stop (stop-hook.sh + chime.sh), UserPromptSubmit, SessionStart. Closing echo: "Done. Pulsar's hooks are removed; non-Pulsar hooks and the status line are untouched." `install-hooks.sh` wires the same 6 (Stop×2 lines 121-122, SessionStart 123, UserPromptSubmit 124, SubagentStart/Stop 125-126) — lists agree. |
| 5 | Tests 70/0, cast-check PASS | **VERIFIED** | Both re-run post-deletion (see Job A verification above); pre-deletion state was identical since deleted files had zero callers. |

## New findings

None beyond the planned Job A deletion. No wrong or incomplete covers found
in cycle 3's claims.

## Lens status

**Dry.** Every claim checked out; the one observation worth logging (the
disclaimer's top-of-tab placement) is a documented trade-off, not a bug —
noted for the record, not raised as a finding to fix.
