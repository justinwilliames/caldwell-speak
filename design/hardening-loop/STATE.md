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
