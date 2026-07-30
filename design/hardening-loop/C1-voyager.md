# C1 Engineering — Voyager (Adversarial Reviewer B): state, persistence, data integrity

**Verdict:** the four sync-twin script pairs have ZERO byte drift (verified) — but the twin
*itself* is the bug: both paths are live-wired into `~/.claude/settings.json` simultaneously,
causing every Pulsar hook to fire twice per event. Found one more CONFIRMED code-level race in
`PulsarConfig.set()`. Drone persistence (`drones.json`), speech.jsonl, and the daemon token are
solid — already hardened from prior rounds.

## CONFIRMED

### 1. Every Pulsar hook is double-registered and double-fires — live, right now
`~/.claude/skills/pulsar` is a symlink to `/Users/justin/code/pulsar` (`readlink` confirms).
`install-hooks.sh`'s `ensure()` dedups by exact string match on `command`
(`/Users/justin/code/pulsar/scripts/install-hooks.sh:67-76`), which does not resolve symlinks.
Having been run once from each path, `~/.claude/settings.json` now carries **two** hook entries
per event, both resolving to the byte-identical file:
- `SubagentStart`: `.../code/pulsar/scripts/subagent-start.sh` + `.../skills/pulsar/scripts/subagent-start.sh`
- `SubagentStop`: same pair
- `Stop`: `stop-hook.sh` x2 **and** `chime.sh` x2
- `UserPromptSubmit`: `turn-start.sh` x2
- `SessionStart`: `session-start-voice.sh` x2

Failure scenario, concretely: `chime.sh` (`/Users/justin/code/pulsar/scripts/chime.sh`) has no
debounce logic (`grep` for recent/busy/dedup — nothing) and is wired to `Stop` twice → an
audible double-chime on every single turn end. `subagent-start.sh`/`subagent-stop.sh` double-POST
`/subagent/start` and `/subagent/stop` for every sub-agent spawn/stop, doubling daemon HTTP load
and (on unresolved categories) doubling the detached `--upgrade` background pollers spawned at
`subagent-start.sh:261`. `stop-hook.sh` is the one script that survives this cleanly — it has an
explicit `/queue` busy-check + `/history` 60s-recent debounce (`stop-hook.sh:73-101`) that was
apparently built for exactly this kind of double-fire, so it usually self-suppresses the second
invocation rather than double-recording into `speech.jsonl`. `turn-start.sh` just overwrites a
timestamp file twice — harmless.

**Minimal fix:** `ensure()` in `install-hooks.sh` should compare `realpath(command)`, not the raw
string, before appending. Immediate operator fix: strip the four `~/.claude/skills/pulsar/scripts/*`
entries from `settings.json` (they're a symlink of the repo copy, contribute nothing, and are the
concrete cause of the chime double-fire happening today).

### 2. `PulsarConfig.set()` — read-modify-write race on concurrent `/settings` POSTs
`macos/Pulsar/Sources/Engine/PulsarConfig.swift:174-180`. The doc comment claims "Thread-safe: all
mutations go through an NSLock," but the lock only guards the in-memory `_config` dict swap inside
`reload()`. `set()` itself does `loadCoerced()` (unlocked file read) → mutate local dict → unlocked
`data.write(to:)` → `reload()`. Two concurrent `handleSettingsPost` calls (Hummingbird runs request
handlers as concurrent Swift Tasks; `handleSettingsPost` is `nonisolated async`,
`PulsarHTTPServer.swift:703`) racing on different keys is a classic lost-update: both read the same
starting file, both write their own key back, and whichever write lands second silently discards
the first's key. Failure scenario: session A POSTs `{"muted": true}` while session B POSTs
`{"expletives_enabled": true}` within the same few milliseconds (plausible — multiple parallel
Claude Code sessions each probe/toggle `/settings`, matching the operator's normal parallel-session
pattern) → one of the two toggles is silently lost from `config.json`, though the losing caller's
in-process `reload()` still reflects it until the next reload from disk.

**Minimal fix:** wrap the read-mutate-write body of `set()` in the existing `lock` (or serialize
`/settings` POSTs through an actor) so the file round-trip is atomic, not just the dict swap.

## PLAUSIBLE (not chased to ground)
- `speech.jsonl` (23KB today, append-only, never rotated, nothing reads it back) will grow
  unbounded forever — not a correctness bug, but no cap/rotation exists.
- `subagent-start.sh:242`'s diagnostic payload dump (`~/.claude/pulsar-last-subagent-payload.json`)
  is a plain `>` overwrite with no lock; concurrent spawns can interleave/truncate it. Explicitly
  a "last one wins" diagnostic by design, so low stakes.

## What I could not break
`drones.json` persistence (atomic `.write(options: .atomic)`, actor-serialized, real-`lastSeen`
restore-then-sweep) is properly hardened. `speech.jsonl`'s own concurrent-append path is correctly
locked (`DaemonAuth.swift:227-253`, single `NSLock` around seek+write). Daemon token perms are
0600/0700 as documented. All four script pairs are byte-identical — no content drift anywhere.
