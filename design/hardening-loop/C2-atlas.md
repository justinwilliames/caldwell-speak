# Cycle 2 — Atlas (naive-user first-principles), re-run

**Verdict:** Not dry. 3 CONFIRMED, 1 PLAUSIBLE. The core install/uninstall flow is honest and idempotent, but the DMG-only path — the one README sells as "no repo, no Terminal" — silently under-delivers one shipped feature, and two docs actively mislead a new user troubleshooting sound/uninstall.

## CONFIRMED findings (ranked)

### 1. In-app installer never copies the pulsar-team skill, though the app stages it specifically to be installed
`macos/Pulsar/Sources/Engine/ClaudeIntegrationInstaller.swift:85-93` (`scriptNames`/`rootFiles`) and `copyPayload()` (182-213) only copy `SKILL.md`/`CANON.md`/`voices.json` to `skillDir` and the 9-item `scriptNames` list to `scriptsDir`. Neither array, nor any other code in the file, ever touches `payloadDir/skills/pulsar-team`. Yet `scripts/build-pulsar-app.sh:44-50` explicitly `mkdir -p`s and `cp`s `pulsar-team/SKILL.md` + scripts into `Resources/claude-integration/skills/pulsar-team` on every build — I verified the staged copy is present and byte-identical to the live skill. `git log -p` on the Swift file confirms it has **never** referenced `pulsar-team`, back to when the staging step was added (commit `8c44875`, "build-pulsar-app.sh: stage pulsar-team SKILL.md + scripts into the claude-integration payload").

**What the new user experiences:** clicks "Set up Pulsar in Claude Code" (the one-click, no-Terminal path README sells), restarts Claude Code — the voice/drone-swarm hooks all work, but `~/.claude/skills/pulsar-team` is never created. `/pulsar-team`, "run the pulsar team," any "send this to the drones" trigger — silently absent. No error, no partial-install notice; the feature just doesn't exist for them, forever, no matter how many times they re-click Setup.

**Minimal fix:** add `"pulsar-team"` handling to `copyPayload()` — either add a `subdirNames`-style loop that recursively copies `payloadDir/skills/*` into `claudeDir/skills/`, or add pulsar-team's two files to `rootFiles`/`scriptNames` with a distinct destination. Cheap, ~10 lines.

### 2. docs/SETUP_MAC.md's voice-roster table is stale and actively wrong, not just incomplete
`docs/SETUP_MAC.md:118-136` lists 7 characters and says "All seven are standard macOS system voices." Actual live cast per `DroneRegistry.swift:83-104` is 9 (Pulsar + 8 drones): the table omits **Iris** and **Meridian** entirely, and — worse — lists **Echo → Tessa (en-ZA)**, which is wrong: the code comment at `DroneRegistry.swift:72-74` says Iris "took Tessa from Echo in the 2026-07-20 stock-voice shuffle"; Echo's actual current voice is **Junior (en-US)** (line 71). The "standard voices" claim is also false for 2 of the cast — Junior and Ralph are explicitly "legacy but whitelisted" MacinTalk voices per the same file's comments, not stock.

**What the new user experiences:** troubleshooting "why don't I hear Iris/Meridian" or trying to pre-install a voice via System Settings → Manage Voices gets no guidance for 2 real drones, and wrong guidance for a 3rd (told to look for Tessa when Echo actually speaks as Junior).

**Minimal fix:** regenerate the table from `DroneRegistry.swift:83-104` (9 rows, correct voice per drone, correct legacy/standard flag).

### 3. scripts/uninstall-hooks.sh only reverses 2 of the 6 hooks the in-app "Remove Pulsar" button removes
The in-app button (`SettingsView.swift:77`, labelled **"Remove Pulsar from Claude Code"**) calls `installer.uninstall()`, which strips all 6 managed hooks + statusLine (`ClaudeIntegrationInstaller.swift:242-249`). But the shipped `scripts/uninstall-hooks.sh` — which `ClaudeIntegrationInstaller.swift:89-91` frames as existing "so a user who wants to reverse the wiring by hand has the script locally (the in-app... button is the primary path)," i.e. positioned as the manual equivalent — by its own header only removes `SubagentStart`/`SubagentStop` (the two drone hooks). `Stop` (voice+chime), `SessionStart`, `UserPromptSubmit`, and `statusLine` all survive a run.

**What the new user experiences:** a user without the app running (or preferring Terminal) runs the "manual reversal" script expecting parity with "Remove Pulsar," restarts Claude Code, and Pulsar still speaks at every turn-end and still owns the status line — looks like the uninstall silently failed.

**Minimal fix:** either rename/re-scope the shipped script's stated purpose (drop the "reverse the wiring by hand" framing in the Swift comment — it isn't), or extend uninstall-hooks.sh to strip all 6 + statusLine like the in-app path does.

## PLAUSIBLE (one-liners)
- `install-hooks.sh`'s realpath-dedup (`_canon()`) has no equivalent doubled-entry protection in `uninstall-hooks.sh`'s `matches()` — not needed today (suffix match already collapses both spellings) but worth a comment noting the asymmetry is intentional, in case a future duplicate-detection change lands in only one script.

## What held up
- Token gate: probed live with `PULSAR_TOKEN_FILE=/nonexistent` against a running daemon — `say.sh` correctly warns on stderr ("the daemon is up and WILL reject this line (401)") rather than failing silently; `DaemonAuth.ensureToken()` runs before the listener is armed, so there's genuinely no unenforced window. Claim holds.
- README's step-4 hook list (7 items) matches `install-hooks.sh` and `ClaudeIntegrationInstaller.swift`'s `managedHooks` exactly.
- No `pretooluse.sh` references anywhere live (only in this hardening log's own history note).
- No stale Missions/ElevenLabs/metered-voice user-facing claims; "eight drones" language in README/pulsar-team SKILL.md is current and correct (8 sub-agent drones + Pulsar = 9).
- Quarantine/xattr step and DMG-vs-source distinction in README + SETUP_MAC.md are accurate and consistent.
