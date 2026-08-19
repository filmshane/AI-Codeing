# Lisa

Prompt: lisa-market-research.system.md

Handoff API:
- GET  http://127.0.0.1:8792/api/voice/lisa/checklist/{lead_id}
- POST http://127.0.0.1:8792/api/voice/lisa/handoff/{lead_id}

On success: Retell dial + CRM status CURR_ALEX
