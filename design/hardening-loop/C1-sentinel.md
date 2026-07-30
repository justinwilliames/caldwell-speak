# C1 — Sentinel (Reviewer A, Engineering)

**Verdict: the auth layer holds under live attack; the new "mute is pause" promise is only half-true, and CI has been RED for every commit shipped today — nothing shipped today has passed its own gate.**

7 CONFIRMED · 4 PLAUSIBLE

## CONFIRMED

**1. CI red on all three of today's commits — the cast gate never ran (high)**
`.github/workflows/build.yml:70` — `python3 -m pip install --quiet Pillow`. Homebrew python3 on `macos-26` is PEP 668 externally-managed; pip refuses. Observed (`gh run view 30512988739`): `Build` ✓, `Run tests` ✓, **`Install Pillow` ✗**, `Cast-consistency check` skipped. Same on `30507920891` and `30515240426` — red since `2a7d52a`.
*Scenario:* the audio-queue rewrite and the auth layer landed on main red; the cast assertion never ran on them, and a real regression is now indistinguishable from the standing red. *Fix:* add `--break-system-packages` (or a venv).

**2. Unmute after >60 s destroys every "held" line (high)**
`AudioQueueActor.swift:849` (`resumeAfterUnmute`) · `:755` purge gate · `:954` worker purge. `resumeAfterUnmute` re-arms the worker but never re-stamps `lastDrainProgressAt`. Nothing makes drain progress while paused, so on re-entry `now - lastDrainProgressAt > 60` opens the gate and every held non-priority waiter older than 60 s is purged immediately.
*Scenario:* mute at T0 with 9 roll-call lines held, unmute at T0+65 s → log says `resuming 9 held line(s)`, all 9 die milliseconds later. Exactly the shared-daemon case `muteNow`'s comment (`:833-840`) claims to fix, and the threshold is 60 s, not "lunch". `DroneLifecycleTests.swift:240` asserts the hold; nothing asserts the resume. *Fix:* `lastDrainProgressAt = Date()` atop `resumeAfterUnmute()`.

**3. say.sh documents a fail-open window that does not exist (medium-high)**
`scripts/say.sh:11-13` claims *"the daemon only enforces once it has a token, so a token-less client still works in that window."* False — `DaemonAuth.token` (`:84-86`) calls `ensureToken()`, which mints **on demand**; the gate is armed from request one.
*Observed:* `PULSAR_TOKEN_FILE=/nonexistent ./scripts/say.sh "…"` → `/health` 200 (exempt), `POST /speak` **401**, say.sh **exit 0, no stderr**, no `speech.jsonl` record. Voice goes permanently silent with zero diagnostic whenever the token file is unreadable — deleted `~/.pulsar`, or a launchd client with a different `HOME`. *Fix:* warn on stderr when health is up but the token is empty; delete the false comment.

**4. `audioDuration` blocks the actor with `waitUntilExit()` (medium)**
`:1396`, called actor-isolated from `playEntry` at `:1163`. Its own doc-comment (`:1386`) says wrap it in `Task.detached`; the sibling `extractEnvelope` **is** wrapped (`:1165`). This is the blocking-syscall-on-a-cooperative-thread pathology the file names as root cause of the old "stops after 2 lines" stall (`:1204-1218`).
*Scenario:* every line parks the actor's executor for an `afinfo` spawn — `/speak`, `/queue`, mute and the drone sweep stall behind it. *Fix:* wrap in `Task.detached`, mirroring `:1165`.

**5. Mute during the fetch wait still destroys the line (medium)**
`:1132-1143`. The worker dequeues then awaits synthesis for up to 30 s (`:933`); a mute in that window hits `playEntry`'s guard, which **drops** the entry (unlinks the AIFF, no history). "Mute is pause" doesn't cover the in-flight line. *Fix:* re-insert at the head of `queue`.

**6. `/queue` reports `paused: false` unconditionally (low-medium)**
`:920-921` hardcodes `paused: false, channelPaused: []`. A muted daemon holding 9 lines reports `playing:false, queued:9, paused:false` — no client can tell paused from wedged. *Fix:* `paused: PulsarConfig.shared.isMuted`.

**7. `speech.jsonl` grows without bound (low)**
`DaemonAuth.swift:67, 200-254` — append-only, no rotation, no cap; 102 records / 24 KB in one day. Perms and disclosure are fine; growth is the defect. *Fix:* roll past ~5 MB.

## PLAUSIBLE

- `ensureToken()` (`:98`) never caches a nil result → a broken `$HOME` retries `createDirectory`+`createFile` **per request**, gate open.
- `runWorker` (`:1045`) recurses into itself on the shutdown re-arm; a sustained enqueue race grows the stack.
- The effective-end cutoff `Task` (`:1235-1238`) is never cancelled; it can fire after its process is reaped and `currentProcess` reassigned.
- `ISO8601DateFormatter()` constructed per speech record (`:211`), inside the write lock.

## What I could not break

- **Both auth gates hold live** (probed at `127.0.0.1:7865`): `/history` no token → **401**, with token → **200**; `Host: evil.example.com` + valid token → **400**; `/health` no token → **200** by design. Both R3 observations are genuinely closed.
- **Middleware ordering is correct:** `router.add(middleware:)` precedes `registerRoutes` (`PulsarHTTPServer.swift:108`), so 404s and future routes are gated by default; `ensureToken()` runs in `configure()` (`:42`), awaited by `startup()` before `start()`. Perms on disk: `~/.pulsar` `drwx------`, `daemon-token` `-rw-------` (64 hex), `speech.jsonl` `-rw-------`.
- **`macos-26` is a real label, not aspirational** — runner reported `ProductVersion: 26.4`, precheck passed, `swift build -c release` and `run-tests.sh` both succeeded on it. Only the Pillow step is broken.
- **All 15 client scripts are token-aware** (9 in `scripts/`, 6 bundled), every bundled copy **byte-identical** to its repo-root canonical. In-app clients authorize too — `DaemonAPI:22`, `PortraitManager:73`, `SSEClient:62` (read per-connect) — no 401 loop for head, subtitles, or portraits.
- **Missions excision is clean** — no route, config key, or residual symbol in any `*.swift`/`*.sh`/`*.json`.
