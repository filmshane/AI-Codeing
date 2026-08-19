# Comp AI CRM + Hermes Reed

Upstream: https://github.com/trycompai/crm (release branch)

## What runs

| Unit | Port | Role |
|---|---|---|
| docker `crm-postgres` | 5432 | Postgres |
| `compai-crm-api` | 3001 | Nest API |
| `compai-crm-app` | 3010 | Next.js UI (not 3000; Open WebUI keeps 3000) |
| `compai-crm-hermes` | 2000 | Reed — Hermes decision agent (replaces eve) |

UI: http://127.0.0.1:3010

## Agent

Reed (`/opt/compai-crm-hermes/reed.system.md`) uses the FPI RISEN template.
LLM: Hermes Grok via `127.0.0.1:8645`. Evidence rule: nothing about a person is guessed.

Prompt copy: `/home/shanem/FPI-Corp/A-Prompts/reed-crm-decision.system.md`

## Sign-in

Needs Google or Microsoft OAuth in `/opt/compai-crm/.env`, or:

```
cd /opt/compai-crm
ALLOWED_SIGN_IN already has shane.a.miller@live.com
bun run --filter=api dev:session
```

`dev:session` mints a cookie without an identity provider (local only).

## Commands

```
sudo systemctl status compai-crm-app compai-crm-api compai-crm-hermes
curl -s http://127.0.0.1:2000/health
docker compose -f /opt/compai-crm/docker-compose.yml ps
```
