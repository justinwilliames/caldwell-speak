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
