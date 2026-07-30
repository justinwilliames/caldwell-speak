# Cycle 3 — Nova (UX/product lens), commit 762069e

**Verdict:** Ship-quality craft, one self-defeating placement bug and one real
crowding bug at scale. The new fictional-persona disclaimer is real copy in the
right component but the LEAST visible text in the popover — buried below the
fold in the lowest-contrast style available. The floating swarm's "quiet" idle
state was explicitly hardened for all 9 characters; its "busy" active-speaker
state (the one that actually matters — someone talking while several drones
work) was not, and visibly crowds. Settings, tabs, and the base subtitle bubble
are clean.

## Confirmed findings (ranked)

**1. The persona disclaimer is placed exactly where it won't be read.**
Evidence: `Sources/Views/Popover/RosterView.swift:63-74`; screenshots
`popover1.png` → `popover5.png` (live popover, Team tab, default on open).
Team is the default tab (`PopoverRootView.swift:58`), so a new user's first
screen is the roster — but the disclaimer sits *after* all 9 cast cards
(Pulsar + 8 drones), reachable only after ~3 scroll actions, and is rendered
in `.tertiary` + `.caption2` — the smallest, lowest-contrast text style used
anywhere in this view (every other label in the popover is `.secondary` or
`.primary`). Zoomed crop (`disclaimer_zoom.png`) confirms it reads as faint
grey-on-grey. Consequence: the one piece of copy whose entire job is telling
every user "these characters are invented, not real people" is the single
least-likely string in the app to actually be seen. Fix: move it directly
under the "MEET THE TEAM" header (above the cast list, not below), and bump
to `.secondary` — informational copy that only works if read shouldn't use
the app's most easily-skipped style.

**2. Active-speaker swarm crowds and self-occludes at realistic drone counts.**
Evidence: `Sources/Views/Floating/FloatingHeadsView.swift:279-334` (arc mode,
`orbitAngle`/`clusterStepDegrees:44°`/`orbitRadius:80`, no cap on orbit slots)
vs. `:230` (`dedupedQueuedItems` explicitly caps at `.prefix(5)`); live
screenshots `swarm4.png`/`swarm4_zoom.png` with 8 real in-flight drones
(seeded via `/subagent/start`) + Sentinel speaking centre. Several orbit
portraits are reduced to a sliver, stacked behind the much-larger centre
head and each other — exactly the scenario `pulsar-team`'s 8-drone review
produces. By contrast the IDLE cluster (`symmetricClusterOffsets`, same
file `:521-557`) was deliberately hardened for this — the code comment
even says "a full nine-drone review — Meridian included — packs without any
slot falling off the table" — and `swarm2.png`/`swarm3.png` confirm a clean,
non-overlapping 3×3 grid at rest. So the quiet state is the polished one and
the busy, information-dense state (which is when a user most needs to read
who's doing what) is the messiest. Fix: give arc mode the same treatment —
either a count-aware step/radius, or cap visible orbit slots (mirroring the
existing 5-item cap on `dedupedQueuedItems`) with a "+N" overflow badge.

## Plausible (not chased further)

- `Sources/Views/Popover/HistoryPanelView.swift`, `QueuePanelView.swift`,
  `NowPlayingView.swift` are never instantiated anywhere (`grep -rn
  "HistoryPanelView(|QueuePanelView(|NowPlayingView("` → zero hits outside
  their own file); only a stray comment in `PortraitView.swift:20` still
  names them. No user-visible harm today, but likely dead weight from before
  the Missions excision — worth a follow-up prune.

## What looked right

- `PopoverRootView` has exactly two live tabs (Team, Settings) — no orphaned
  Missions tab, no dead nav state.
- `SettingsView`: dependent toggles correctly disable (Subtitles/Show active
  agents both require Floating head, with the reason stated inline);
  recovery banners (muted, basic-voice) are genuinely actionable, not just
  informative; register picker and persona-copy button both work as shown.
- `SubtitleBubbleView`: legible white-on-tinted-glass at every size, the
  typewriter reveal reads naturally even mid-reveal, and `say.sh`'s 200-char
  cap cuts at a sentence/word boundary with no ellipsis — a truncated line
  never looks broken.
- The idle 9-character cluster is a genuine craft win — clean, symmetric,
  zero overlap, verified live.
