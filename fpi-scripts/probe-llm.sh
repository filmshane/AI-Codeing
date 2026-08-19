#!/usr/bin/env bash
# Smoke-test FPI LLM path (Hermes proxy + grok-4.20-reasoning). No secrets printed.
set -euo pipefail
BASE="${FPI_LLM_BASE_URL:-http://127.0.0.1:8645/v1}"
MODEL="${FPI_LLM_MODEL:-grok-4.20-reasoning}"
KEY="${FPI_LLM_API_KEY:-hermes-proxy}"

code=$(curl -sS -m 60 -o /tmp/fpi-llm-probe.json -w '%{http_code}' \
  "$BASE/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KEY" \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Say only: FPI-LLM-OK\"}],\"max_tokens\":32}")

echo "http=$code model=$MODEL base=$BASE"
python3 - <<'PY'
import json
from pathlib import Path
d=json.loads(Path('/tmp/fpi-llm-probe.json').read_text())
if 'choices' in d:
    print('content=', (d['choices'][0].get('message') or {}).get('content','')[:120])
else:
    print('error_keys=', list(d)[:8])
PY
