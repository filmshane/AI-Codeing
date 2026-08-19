# FPI CRM

**Path:** `/home/shanem/FPI-Corp/CRM/`

# FPI CRM + website lock-in

## CRM (v3)

| Path | Use |
|------|-----|
| `/home/shanem/FPI-Corp/CRM/fpi_crm.db` | SQLite DB |
| `schema.sql` | Full field schema |
| `init_crm.py` | Rebuild + seed |
| `crm_report.py` | Full-field report |
| `STATUS-PIPELINE.md` | Stage definitions |
| `CRM-REPORT-LATEST.txt` | Last generated report |

```bash
cd /home/shanem/FPI-Corp/CRM
python3 init_crm.py
python3 crm_report.py                    # all leads
python3 crm_report.py -o CRM-REPORT-LATEST.txt
```

### Stages
NEW_LISA_LEAD → APPROVED_LEAD_SENDING_ALEX → CURR_ALEX → SCOUTING_LEAD → WAITING_MAX_PRICE_SHANE → ALEX_MANAGING → CLIENT_APPROVED_CONTRACT_PENDING → CONTRACT_SIGNED → FINDING_FLIPPER → ASSIGNED_TO_FLIPPER → CLOSED

Field **`qualified`**: Y / N (Alex sets before Scout).

### Demo lead
`lead-1513-18th-st-nw-cleveland` @ **WAITING_MAX_PRICE_SHANE**, qualified=Y

## Website

Live: http://firstpropertyinvestment.us/

- AI disclosure checkbox + call preference on form
- Chatbot bottom-right (name → phone → address → POST send.php)
- `send.php` emails Shane + appends `/var/www/firstpropertyinvestment.us/leads-inbox/leads.jsonl`
- Deploy script: `/var/www/firstpropertyinvestment.us/ (HTML never moved; deploy script may live under Projects website-fpi staging only)` (run as root)

## Agents
Working dirs: `/home/shanem/FPI-Corp/{Lisa,Alex,Scout,Ryan,Atlas,Blake}/`  
Prompt index: `/home/shanem/FPI-Corp/A-Prompts/`  
Scout helpers: `/home/shanem/FPI-Corp/Scout/scout_*.py` (CRM has shims)
