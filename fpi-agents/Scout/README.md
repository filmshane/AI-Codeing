# Scout — Comps / rehab / MAO + DEAL RECAP

## Prompt
- `scout-deal-analyzer.system.md`
- `SCOUT-DEAL-RECAP-TEMPLATE.md`

## Helpers
- `scout_redfin_comps.py` — Redfin subject + sold-filter comps
- `scout_deal_recap.py` — Low/Med/High DEAL RECAP builder

```bash
python3 scout_deal_recap.py 429000 120000
python3 scout_redfin_comps.py --help
```

## Model
- **LLM:** `grok-4.20-reasoning` (Grok 4.2 Reasoning)
- **Auth:** Hermes xAI OAuth via `hermes-proxy-xai` `http://127.0.0.1:8645/v1`
- **Config:** `/home/shanem/FPI-Corp/config/llm.json` + `config/llm.env`
