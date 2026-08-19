#!/usr/bin/env bash
# Sync Hermes SuperGrok / xAI OAuth access token into FPI-Corp data dir.
# Same pattern as receipt-bot: token file mode 600, re-read per request.
set -euo pipefail

OUT_DIR="${FPI_DATA_DIR:-/home/shanem/FPI-Corp/data}"
OUT_FILE="${OUT_DIR}/xai_access_token"
PY="${HERMES_PYTHON:-/home/shanem/.hermes/hermes-agent/venv/bin/python}"
LOG="${OUT_DIR}/xai-oauth-sync.log"

mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR" 2>/dev/null || true

if [[ ! -x "$PY" ]]; then
  echo "$(date -Is) ERROR: hermes venv python missing: $PY" | tee -a "$LOG" >&2
  exit 1
fi

TOKEN="$("$PY" - <<'PY'
from hermes_cli.auth import resolve_xai_oauth_runtime_credentials
c = resolve_xai_oauth_runtime_credentials(refresh_if_expiring=True)
key = (c or {}).get("api_key") or ""
if not key:
    raise SystemExit("no api_key from resolve_xai_oauth_runtime_credentials")
print(key, end="")
PY
)"

tmp="${OUT_FILE}.tmp.$$"
printf '%s' "$TOKEN" >"$tmp"
chmod 600 "$tmp"
mv -f "$tmp" "$OUT_FILE"

# length only — never log token
echo "$(date -Is) synced xai_access_token len=${#TOKEN} -> $OUT_FILE" >>"$LOG"
echo "ok len=${#TOKEN}"
