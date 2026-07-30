# Pulsar — Privacy Posture

One page, written to be checked rather than trusted. Every claim below is verifiable
against the source in this repository.

## What Pulsar does with your data

- **Voice is 100% local.** Every spoken line is synthesised on your machine by the
  built-in macOS `say` engine. No account, no API key, no speech service, no network
  call. (Verify: `grep -r "https://" macos/Pulsar/Sources` — the daemon makes no
  outbound requests.)
- **No telemetry.** Pulsar collects no analytics, sends no usage data, and phones
  nothing home. There is no tracking code to opt out of because there is none at all.
- **The only outbound connection is the update check.** Sparkle asks
  `github.com` whether a newer release exists (`SUFeedURL` in `macos/Pulsar/Info.plist`).
  Sparkle requests your permission for this on first launch; decline it and the only
  update check is the one you trigger yourself via "Check for Updates…".

## What stays on your machine

- **Spoken-line history** lives in the app's memory (bounded) and in an append-only
  local log at `~/.pulsar/speech.jsonl` — created by you, readable by you, never
  transmitted.
- **The local daemon** (`127.0.0.1:7865`) binds to loopback only and requires a
  per-install token (`~/.pulsar/daemon-token`, created `0600`) on every route except
  `GET /health`. Requests with a non-local `Host` header are rejected. Your own
  hooks and scripts read the token file; nothing off your machine can.

## What Pulsar never has

No credentials, no message content from your conversations beyond the lines you route
to it for speech, no contacts, no files, no cloud copy of anything.

*Questions or a claim that doesn't hold? Open an issue — a privacy claim that can't
survive an issue tracker isn't one.*
