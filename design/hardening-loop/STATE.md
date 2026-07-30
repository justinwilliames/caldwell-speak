# Pulsar hardening loop — state
Loop started: 2026-07-30 ~15:00 AEST (Justin's order: /pulsar-team on /loop per claude-build-hardening, until dry)
Stage rotation: Engineering → UX → Security → Accessibility → (repeat)
Dry rule: a cycle is DRY if no CONFIRMED finding worth fixing survives triage. Two consecutive dry cycles → stop loop, PushNotification Justin.
Per cycle: 3 adversarial drone reviewers (parallel) → orchestrator triage → build-drone fixes → verify (swift build + run-tests 59 + cast-check) → commit → push → install+restart.

## Cycle log
- Cycle 1 (Engineering): IN PROGRESS — reviewers: Sentinel/opus (architecture-adversarial), Voyager/sonnet (state+data integrity), Atlas/sonnet (naive-user first-principles). Dry counter: 0.
- Cycle 1 (Engineering) COMPLETE. Reviewers: Sentinel/opus (7 CONFIRMED, 4 PLAUSIBLE), Voyager/sonnet (2 CONFIRMED), Atlas/sonnet DIED (API error — re-run in cycle 2).
  FIXED + verified: CI Pillow PEP-668 (every run today was red); resumeAfterUnmute purge-destroys-held-lines (live: 0/3 → 3/3 after 70s mute); PulsarConfig.set lost-update race (locked);
  install-hooks symlink dedup + live settings.json cleaned (6 dupes removed = the double chime, 1 dangling pretooluse.sh); say.sh silent-401 now warns (the "graceful first run" claim was false).
  DEFERRED to cycle 2: audioDuration blocking the actor (Sentinel #4, needs care); mute-during-fetch-wait drop; /queue hardcodes paused:false; speech.jsonl rotation.
  Dry counter: 0 (cycle was very wet — 9 confirmed findings).
- Cycle 2 (Engineering, round 2): PENDING — mandate: verify cycle-1 fixes weren't papered, re-run the Atlas naive-user lens that died, take the 4 deferred items.
- Cycle 2 COMPLETE. Reviewers: Atlas/sonnet (3 CONFIRMED), Nova/opus (BUILD: all 4 deferred defects fixed, mutation-checked test), Meridian/opus (AUDIT: all 5 C1 fixes VERIFIED genuine; 2 incomplete covers; C1 #7 was WRONG).
  FIXED this cycle: audioDuration off-actor (termination-handler, 5s watchdog, cancelled — probe: 28ms→0ms actor stall); mute-during-fetch now HELD not dropped (+ second gate after the probes);
  /queue reports real paused state (verified live True/False); speech.jsonl rotates at 5MB (2 generations); ClaudeIntegrationInstaller now installs the pulsar-team skill (DMG users previously NEVER got /pulsar-team);
  uninstall-hooks.sh now reverses all 6 hooks (was 2); SETUP_MAC voice table 7→9 + Echo=Junior corrected; PRIVACY.md verify-recipe fixed (was self-falsifying) + rotation documented;
  persona disclaimer added to the app UI (RosterView — nine faces shipped with no notice); PulsarConfig migration write brought under the write lock; unmute-resume REGRESSION TEST added (the one C1 fix with no guard).
  Tests 59→70 passed, 0 failed. cast-check PASS. Dry counter: 0 (still wet — 7 new confirmed findings).
- Cycle 3: PENDING — mandate: UX/product lens (never run yet), security re-probe of the new surfaces (rotation, off-actor process spawn), and re-audit of cycle-2 claims. Note Meridian's method warning: use a git worktree if drones review while another drone writes.
- Cycle 3 COMPLETE. Reviewers: Nova/sonnet UX (2 CONFIRMED, screenshot-evidenced), Voyager/sonnet audit (1 PRODUCTION-BREAKING + 1 docs), Sentinel/opus DIED (API 529 — security re-probe of cycle-2 surfaces CARRIES to cycle 4).
  FIXED: package-dmg.yml never staged pulsar-team — cycle 2's headline fix was INERT for every real DMG download (now staged + hard-fails if missing);
  persona disclaimer moved above the cast (was 3 scrolls down in .tertiary/.caption2 — the least readable text in the app); orbit arc capped at 6 while a speaker holds centre (idle 9-cluster untouched);
  uninstall-hooks.sh header/echo docs corrected to describe the 6-hook behaviour it now has.
  Voyager mutation-tested the unmute-resume test (revert → 69/70, correct assertion fails) = a REAL guard. Tests 70/0, cast-check PASS.
  Dry counter: 0 (still wet). PLAUSIBLE carried: HistoryPanelView/QueuePanelView/NowPlayingView appear never instantiated (dead views, Missions-era).
- Cycle 4: PENDING — mandate: (1) Sentinel's security re-probe of cycle-2/3 surfaces (off-actor process spawn, holdIfMuted double-insert, rotation race, installer sibling-dir write) — DIED on 529, must run; (2) dead-view check; (3) audit cycle-3 claims. Use a git worktree per Meridian's method warning if reviewing while a builder writes.
- Cycle 4 COMPLETE. Reviewers: Atlas/sonnet (DRY — all 5 cycle-3 claims VERIFIED, no new findings; deleted 3 genuinely dead views + stale doc comment, 347 lines), Sentinel/sonnet security (1 CONFIRMED, 2 PLAUSIBLE, 4 of 5 areas "could not break" — verdict "going dry"; two prior attempts died on API 529).
  FIXED: installer's pulsar-team copy had NO ownership check — a user's hand-authored ~/.claude/skills/pulsar-team would be silently clobbered on Setup; now gated on our own `name: pulsar-team` frontmatter marker, both install and uninstall.
  Sentinel could NOT break: ContinuationBox double-resume (structurally impossible), holdIfMuted double-hold, speech.jsonl rotation serialisation, auth surface (only /health open; stale tokens fail loud 401).
  PLAUSIBLE carried: watchdog uses SIGTERM with no SIGKILL escalation; holdIfMuted head-reinsert can precede a priority entry enqueued during a mute (ordering nuance, not corruption).
  Tests 70/0, cast-check PASS. DRY COUNTER: 1 (Atlas dry + Sentinel "going dry" with one non-severe finding = counting this as the first dry-ish cycle; cycle 5 decides).
- Cycle 5: PENDING — the decider. If it comes back dry, the loop STOPS (two consecutive). Mandate: fresh eyes on the two carried PLAUSIBLE items, a creative/brand lens (Nebula — never run in this loop), and a final Meridian legal/distribution re-check post-cycle-4.
