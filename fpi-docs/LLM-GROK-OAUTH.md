# FPI agents — Grok 4.2 Reasoning + Hermes xAI OAuth

## Locked model
- **Model:** `grok-4.20-reasoning` (aliases: `grok-4.20`, `grok-4.20-reasoning-latest`)
- **Auth:** Same SuperGrok / xAI OAuth Hermes uses (`~/.hermes/auth.json` → `xai-oauth`)

## How it works
1. `hermes-proxy-xai.service` listens on `127.0.0.1:8645`
2. Apps call OpenAI-compatible `POST /v1/chat/completions` with any bearer
3. Proxy attaches live OAuth access token to `api.x.ai`
4. `fpi-xai-oauth-sync.timer` (user) every 3h writes  
   `/home/shanem/FPI-Corp/data/xai_access_token` for daemons that need a file

## Config files
| Path | Use |
|------|-----|
| `/home/shanem/FPI-Corp/config/llm.json` | Canonical model + endpoints |
| `/home/shanem/FPI-Corp/config/llm.env` | Env for agent runtimes |
| `/home/shanem/FPI-Corp/scripts/sync-xai-oauth.sh` | Token sync |
| `/home/shanem/FPI-Corp/scripts/probe-llm.sh` | Smoke test |

## Runtime env (all agents)
```bash
export FPI_LLM_MODEL=grok-4.20-reasoning
export FPI_LLM_BASE_URL=http://127.0.0.1:8645/v1
export FPI_LLM_API_KEY=hermes-proxy
# optional direct:
# export XAI_TOKEN_FILE=/home/shanem/FPI-Corp/data/xai_access_token
# export XAI_BASE_URL=https://api.x.ai/v1
```

## ElevenLabs (Alex voice)
ElevenLabs cloud **cannot** reach `127.0.0.1:8645`.
Options:
1. Public HTTPS reverse-proxy to the Hermes proxy (auth-gated) as **custom LLM**
2. Small public FPI bridge that uses local OAuth proxy and exposes OpenAI schema
3. xAI **console API key** only for ElevenLabs if you will not expose the proxy

Set custom LLM model id to **`grok-4.20-reasoning`**.

## Ops
```bash
systemctl is-active hermes-proxy-xai.service
systemctl --user start fpi-xai-oauth-sync.service
/home/shanem/FPI-Corp/scripts/probe-llm.sh
```

Hermes default CLI model remains whatever `hermes config get model.default` says (currently may still be grok-4.5). FPI agents are pinned separately to **grok-4.20-reasoning**.
