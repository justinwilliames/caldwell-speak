#!/usr/bin/env bash
# say.sh — TTS via the Pulsar app's HTTP server on 127.0.0.1:7865.
# No fallback: if the app (daemon) is down, say.sh stays silent. Voice fires
# only when the Pulsar app is running.

set -euo pipefail

# --- Pulsar daemon auth ------------------------------------------------------
# The app mints a random token into ~/.pulsar/daemon-token (0600) when it starts
# and requires it in the X-Pulsar-Token header on every route except GET /health.
# GRACEFUL FIRST RUN: if the file is absent (app never launched yet) we send NO
# header at all — the daemon only enforces once it has a token, so a token-less
# client still works in that window instead of hard-failing with 401.
PULSAR_TOKEN_FILE="${PULSAR_TOKEN_FILE:-$HOME/.pulsar/daemon-token}"
PULSAR_TOKEN=""
if [ -r "$PULSAR_TOKEN_FILE" ]; then
  PULSAR_TOKEN="$(tr -d '\r\n' < "$PULSAR_TOKEN_FILE" 2>/dev/null || echo "")"
fi
pulsar_curl() {
  if [ -n "$PULSAR_TOKEN" ]; then
    curl -H "X-Pulsar-Token: $PULSAR_TOKEN" "$@"
  else
    curl "$@"
  fi
}
# ----------------------------------------------------------------------------


SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load .env if present (real env vars win via ${VAR:-} pattern)
if [[ -f "$REPO_ROOT/.env" ]]; then
  while IFS='=' read -r key value; do
    key="${key%%#*}"          # strip inline comments
    key="${key// /}"          # strip spaces
    [[ -z "$key" || "$key" == \#* ]] && continue
    value="${value%\"}"       # strip surrounding quotes
    value="${value#\"}"
    value="${value%\'}"
    value="${value#\'}"
    : "${!key:=$value}"       # only set if not already in env
    export "$key"
  done < "$REPO_ROOT/.env"
fi

SPEAK_PORT="${SPEAK_PORT:-7865}"
DAEMON="http://127.0.0.1:$SPEAK_PORT"

# Parse arguments
TEXT=""
VOICE=""
CHANNEL=""
PRIORITY=false
CACHEABLE=false
AGENT=""
ACTION=""
LIMIT=50
REPLAY_ID=""
SETUP_VALUE=""
CANON_CONTEXT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --voice)         VOICE="$2"; shift 2 ;;
    --channel)       CHANNEL="$2"; shift 2 ;;
    --agent)         AGENT="$2"; shift 2 ;;
    --priority)      PRIORITY=true; shift ;;
    --cacheable)     CACHEABLE=true; shift ;;
    --canon)         ACTION="canon"; CANON_CONTEXT="$2"; shift 2 ;;
    --status)        ACTION="status"; shift ;;
    --skip)          ACTION="skip"; shift ;;
    --clear)         ACTION="clear"; shift ;;
    --pause)         ACTION="pause"; shift ;;
    --resume)        ACTION="resume"; shift ;;
    --history)       ACTION="history"; shift ;;
    --limit)         LIMIT="$2"; shift 2 ;;
    --replay)        ACTION="replay"; REPLAY_ID="$2"; shift 2 ;;
    --usage)         ACTION="usage"; shift ;;
    --settings)      ACTION="settings"; shift ;;
    --mute)          ACTION="set-muted"; SETUP_VALUE="true"; shift ;;
    --unmute)        ACTION="set-muted"; SETUP_VALUE="false"; shift ;;
    -*)              echo "Unknown option: $1" >&2; exit 1 ;;
    *)               TEXT="$1"; shift ;;
  esac
done

# Check daemon health
daemon_up() {
  pulsar_curl -sf --connect-timeout 1 "$DAEMON/health" >/dev/null 2>&1
}

# Build JSON body with safe serialization
json_body() {
  python3 -c "
import json, sys
d = {}
if sys.argv[1]: d['channel'] = sys.argv[1]
print(json.dumps(d))
" "$CHANNEL"
}

# Dispatch actions
case "${ACTION:-speak}" in
  status)
    pulsar_curl -sf "$DAEMON/queue" | python3 -m json.tool
    ;;
  skip)
    pulsar_curl -sf -X POST "$DAEMON/queue/skip"
    ;;
  clear)
    pulsar_curl -sf -X POST -H "Content-Type: application/json" -d "$(json_body)" "$DAEMON/queue/clear"
    ;;
  pause)
    pulsar_curl -sf -X POST -H "Content-Type: application/json" -d "$(json_body)" "$DAEMON/queue/pause"
    ;;
  resume)
    pulsar_curl -sf -X POST -H "Content-Type: application/json" -d "$(json_body)" "$DAEMON/queue/resume"
    ;;
  history)
    pulsar_curl -sf "$DAEMON/history?limit=$LIMIT" | python3 -m json.tool
    ;;
  replay)
    REPLAY_BODY=$(python3 -c "import json, sys; print(json.dumps({'id': sys.argv[1]}))" "$REPLAY_ID")
    pulsar_curl -sf -X POST -H "Content-Type: application/json" \
      -d "$REPLAY_BODY" "$DAEMON/history/replay"
    ;;
  usage)
    pulsar_curl -sf "$DAEMON/usage" | python3 -m json.tool
    ;;
  settings)
    pulsar_curl -sf "$DAEMON/settings" | python3 -m json.tool
    ;;
  set-muted)
    BODY=$(python3 -c "import json, sys; print(json.dumps({'muted': sys.argv[1] == 'true'}))" "$SETUP_VALUE")
    pulsar_curl -sf -X POST -H "Content-Type: application/json" -d "$BODY" "$DAEMON/settings" | python3 -m json.tool
    ;;
  canon)
    # Context-aware canon pick. The daemon picks a phrase tagged with the
    # given context and enqueues it, synthesised locally by macOS `say`.
    # Stays silent (HTTP 204) if nothing matches the context. Use this for
    # turn-end pings instead of hand-writing canon strings.
    #
    # Known contexts: push, tests-pass, build-pass, found, fail, done,
    # start, ack, reassure, neutral.
    if ! daemon_up; then
      exit 0
    fi
    BODY=$(python3 -c "import json, sys; print(json.dumps({'context': sys.argv[1]}))" "$CANON_CONTEXT")
    pulsar_curl -sf --max-time 3 -X POST -H "Content-Type: application/json" \
      -d "$BODY" "$DAEMON/canon/pick" >/dev/null 2>&1 || true
    exit 0
    ;;
  speak)
    [[ -z "$TEXT" ]] && {
      echo "Usage: say.sh \"text\" [--voice NAME] [--channel CH] [--agent DRONE] [--priority] [--cacheable]" >&2
      echo "       say.sh --status | --skip | --clear | --pause | --resume" >&2
      echo "       say.sh --history [--limit N] | --replay ID" >&2
      echo "       say.sh --usage | --settings" >&2
      echo "       say.sh --mute | --unmute" >&2
      echo "" >&2
      echo "Add --cacheable for any line generic enough to fire again" >&2
      echo "on a different turn (\"Pushed.\", \"Sorted Sir.\", \"Tests passing.\")." >&2
      echo "Context-specific lines should never be cached." >&2
      exit 1
    }

    # Daemon is the Swift app. If it's not running, stay silent — there is
    # no out-of-app fallback path. Voice fires ONLY when the app is open
    # (popover + voice are a single feature; no daemon = no voice).
    if ! daemon_up; then
      exit 0
    fi

    # say.sh runs INSIDE the sub-agent, so its env carries the session id.
    # Passing it lets the daemon session-scope claim-on-speak promotion — an
    # --agent line only claims a generic drone from its OWN session. Best-effort:
    # absent env → empty → omitted, and the daemon falls back to cross-session.
    SESSION_ID="${CLAUDE_CODE_SESSION_ID:-${CLAUDE_SESSION_ID:-}}"

    # Build JSON body using python3 for safe serialization.
    # CAP FOR LENGTH AT THE SOURCE: a spoken line is a glance, not a paragraph.
    # Trim to <= MAX_SPOKEN_CHARS, cut at the LAST sentence end within the budget
    # (else the last word boundary) so it always ends cleanly — NO ellipsis, ever.
    # Bounds both the audio and the subtitle bubble, so no line from Pulsar OR a
    # drone can overflow or need truncating downstream.
    BODY=$(python3 -c "
import json, sys, re
MAX_SPOKEN_CHARS = 200
text = sys.argv[1]
if len(text) > MAX_SPOKEN_CHARS:
    window = text[:MAX_SPOKEN_CHARS]
    ends = list(re.finditer(r'[.!?](?:\s|\$)', window))
    if ends:
        text = window[:ends[-1].end()].rstrip()
    else:
        sp = window.rfind(' ')
        text = (window[:sp] if sp > 0 else window).rstrip()
d = {'text': text}
if sys.argv[2]: d['voice'] = sys.argv[2]
if sys.argv[3]: d['channel'] = sys.argv[3]
if sys.argv[4] == 'true': d['priority'] = True
if sys.argv[5] == 'true': d['cacheable'] = True
if sys.argv[6]: d['agent'] = sys.argv[6]
if sys.argv[7]: d['session_id'] = sys.argv[7]
print(json.dumps(d))
" "$TEXT" "$VOICE" "$CHANNEL" "$PRIORITY" "$CACHEABLE" "$AGENT" "$SESSION_ID")

    # --max-time guards against curl hanging on a stale keep-alive
    # connection; output redirected to /dev/null so Claude Code's Bash
    # tool sees stdout close immediately. Explicit `exit 0` ensures the
    # shell terminates the moment curl returns.
    pulsar_curl -sf --max-time 3 -X POST -H "Content-Type: application/json" \
      -d "$BODY" "$DAEMON/speak" >/dev/null 2>&1 || true
    exit 0
    ;;
esac
