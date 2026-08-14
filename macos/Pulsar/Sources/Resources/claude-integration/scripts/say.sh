#!/usr/bin/env bash
# say.sh — TTS via the Pulsar app's HTTP server on 127.0.0.1:7865.
# No fallback: if the app (daemon) is down, say.sh stays silent. Voice fires
# only when the Pulsar app is running.

set -euo pipefail

# --- Pulsar daemon auth ------------------------------------------------------
# The app mints a random token into ~/.pulsar/daemon-token (0600) when it starts
# and requires it in the X-Pulsar-Token header on every route except GET /health.
# The daemon mints the token during startup, so the gate is armed from the very
# first request — there is NO unenforced window. A missing/unreadable token file
# therefore means voice is DEAD (every /speak 401s), not "degraded", so warn on
# stderr rather than failing silently: a silent 401 is indistinguishable from a
# muted app (found by adversarial review 2026-07-30, correcting the earlier
# "graceful first run" claim, which was wrong).
PULSAR_TOKEN_FILE="${PULSAR_TOKEN_FILE:-$HOME/.pulsar/daemon-token}"
PULSAR_TOKEN=""
if [ -r "$PULSAR_TOKEN_FILE" ]; then
  PULSAR_TOKEN="$(tr -d '\r\n' < "$PULSAR_TOKEN_FILE" 2>/dev/null || echo "")"
fi
if [ -z "$PULSAR_TOKEN" ] && curl -sf --max-time 1 "http://127.0.0.1:${SPEAK_PORT:-7865}/health" >/dev/null 2>&1; then
  echo "say.sh: no readable token at $PULSAR_TOKEN_FILE — the daemon is up and WILL reject this line (401). Relaunch Pulsar to mint one." >&2
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
SESSION=""
SESSION_REF=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --voice)         VOICE="$2"; shift 2 ;;
    --channel)       CHANNEL="$2"; shift 2 ;;
    --agent)         AGENT="$2"; shift 2 ;;
    --session)       SESSION="$2"; shift 2 ;;
    --session-ref)   SESSION_REF="$2"; shift 2 ;;
    --priority)      PRIORITY=true; shift ;;
    --cacheable)     CACHEABLE=true; shift ;;
    --canon)         ACTION="canon"; CANON_CONTEXT="$2"; shift 2 ;;
    --status)        ACTION="status"; shift ;;
    --stop)         ACTION="stop"; shift ;;
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

# Resolve WHO is speaking-from: the human-readable session NAME, and the id the
# app needs to open that session again (`claude://resume?session=<uuid>`).
# Prints exactly two lines — name, then ref — either of which may be empty.
#
# Name, best source first:
#   1. $CLAUDE_JOB_DIR/state.json  — a background job carries its live name there.
#   2. The Claude Code desktop app's own session record, which is where the
#      TITLE actually lives when Claude Code runs inside the desktop app
#      (~/Library/Application Support/Claude/claude-code-sessions/<a>/<b>/
#      local_<host-session-id>.json). Upstream only had (3), which is silent for
#      every desktop-hosted session — its transcript carries no title record.
#   3. The last aiTitle/agentName record in the CLI transcript (plain CLI runs),
#      so a rename is picked up on the next call.
#
# Ref: the desktop host session id (minus its `local_` prefix) when there is one
# — that focuses the session that ALREADY exists rather than importing a second
# copy of it — else the CLI session id, which the desktop app imports on demand.
# Sub-agents inherit both env vars, so a drone's line attributes to its parent
# session, which is exactly the session a click should land on.
resolve_session() {
  python3 - <<'PY' 2>/dev/null || true
import glob, json, os, re

HOME = os.path.expanduser("~")

def job_name():
    d = os.environ.get("CLAUDE_JOB_DIR")
    if not d:
        return None
    try:
        with open(os.path.join(d, "state.json")) as f:
            return json.load(f).get("name") or None
    except (OSError, ValueError):
        return None

def host_id():
    raw = (os.environ.get("CLAUDE_CODE_HOST_SESSION_ID") or "").strip()
    if raw.startswith("local_"):
        raw = raw[len("local_"):]
    return raw or None

def desktop_title(hid):
    if not hid:
        return None
    hits = glob.glob(os.path.join(
        HOME, "Library/Application Support/Claude/claude-code-sessions",
        "*", "*", "local_%s.json" % hid))
    if not hits:
        return None
    # The record opens with its metadata header (sessionId, cwd, title, …)
    # before the bulky per-session config, so the head is enough — and keeps
    # this cheap on the multi-megabyte records.
    try:
        with open(max(hits, key=os.path.getmtime), "rb") as f:
            head = f.read(65536).decode("utf-8", "replace")
    except OSError:
        return None
    m = re.search(r'"title"\s*:\s*"((?:[^"\\]|\\.)*)"', head)
    if not m:
        return None
    try:
        return json.loads('"%s"' % m.group(1)) or None
    except ValueError:
        return None

def transcript_name():
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not sid:
        return None
    hits = glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % sid))
    if not hits:
        return None
    path = max(hits, key=os.path.getmtime)
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - 262144))
            tail = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    name = None
    for line in tail.splitlines():
        if '"aiTitle"' not in line and '"agentName"' not in line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict):
            name = rec.get("aiTitle") or rec.get("agentName") or name
    return name

hid = host_id()
print((job_name() or desktop_title(hid) or transcript_name() or "").replace("\n", " ").strip())
print(hid or os.environ.get("CLAUDE_CODE_SESSION_ID") or "")
PY
}

# Fill SESSION / SESSION_REF from the environment unless the caller passed them.
# Best-effort: anything unresolved stays empty and is simply omitted from the body.
fill_session() {
  [[ -n "$SESSION" && -n "$SESSION_REF" ]] && return 0
  local resolved
  resolved="$(resolve_session)"
  [[ -z "$SESSION" ]]     && SESSION="$(printf '%s\n' "$resolved" | sed -n 1p)"
  [[ -z "$SESSION_REF" ]] && SESSION_REF="$(printf '%s\n' "$resolved" | sed -n 2p)"
  return 0
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
    # Canon fires from the Stop hook, which runs with the session's env — so the
    # most frequent line of all (the turn-end ping) is attributed too.
    fill_session
    BODY=$(python3 -c "
import json, sys
d = {'context': sys.argv[1]}
if sys.argv[2]: d['session'] = sys.argv[2]
if sys.argv[3]: d['session_ref'] = sys.argv[3]
print(json.dumps(d))
" "$CANON_CONTEXT" "$SESSION" "$SESSION_REF")
    pulsar_curl -sf --max-time 3 -X POST -H "Content-Type: application/json" \
      -d "$BODY" "$DAEMON/canon/pick" >/dev/null 2>&1 || true
    exit 0
    ;;
  speak)
    [[ -z "$TEXT" ]] && {
      echo "Usage: say.sh \"text\" [--voice NAME] [--channel CH] [--agent DRONE] [--session NAME] [--session-ref ID] [--priority] [--cacheable] | --stop" >&2
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

    # ...and the human-readable session NAME plus the id that reopens it, so the
    # app can show WHICH session a drone is speaking from and take you there.
    fill_session

    # Build JSON body using python3 for safe serialization.
    # CAP FOR LENGTH AT THE SOURCE: a spoken line is a glance, not a paragraph.
    # Trim to <= MAX_SPOKEN_CHARS, cut at the LAST sentence end within the budget
    # (else the last word boundary) so it always ends cleanly — NO ellipsis, ever.
    # Bounds both the audio and the subtitle bubble, so no line from Pulsar OR a
    # drone can overflow or need truncating downstream.
    BODY=$(python3 -c "
import json, sys, re
MAX_SPOKEN_CHARS = 200
# Cutting at the last sentence end inside the budget is right ONLY when that
# end sits near the budget. When the line opens with a short sentence ('Done.')
# and the substance runs past the cap, the sentence rule threw the substance
# away and spoke the one word — the line came out mangled, not merely trimmed.
# So: honour a sentence boundary only in the last quarter of the budget,
# otherwise fall back to the word boundary and keep the meaning.
MIN_KEEP = int(MAX_SPOKEN_CHARS * 0.75)
text = sys.argv[1]
if len(text) > MAX_SPOKEN_CHARS:
    window = text[:MAX_SPOKEN_CHARS]
    ends = [m for m in re.finditer(r'[.!?](?:\s|\$)', window) if m.end() >= MIN_KEEP]
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
if sys.argv[8]: d['session'] = sys.argv[8]
if sys.argv[9]: d['session_ref'] = sys.argv[9]
print(json.dumps(d))
" "$TEXT" "$VOICE" "$CHANNEL" "$PRIORITY" "$CACHEABLE" "$AGENT" "$SESSION_ID" "$SESSION" "$SESSION_REF")

    # --max-time guards against curl hanging on a stale keep-alive
    # connection; output redirected to /dev/null so Claude Code's Bash
    # tool sees stdout close immediately. Explicit `exit 0` ensures the
    # shell terminates the moment curl returns.
    pulsar_curl -sf --max-time 3 -X POST -H "Content-Type: application/json" \
      -d "$BODY" "$DAEMON/speak" >/dev/null 2>&1 || true
    exit 0
    ;;
esac
