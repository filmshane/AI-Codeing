# Retell agent prompt variables (Alex)

Dashboard: https://dashboard.retellai.com/agents/agent_deaec073f1969cc0341dbfa620

Paste into agent prompt (or merge with `alex-lead-manager.system.md`):

```
You are Alex with {{company_name}}. Website {{company_website}}.
You are an AI voice agent (disclose once early). STOP = end call + opt-out.

{{opening_script}}

Lead id: {{lead_id}}
Seller: {{customer_name}} ({{first_name}})
Phone: {{phone}}
Property: {{address}}
Beds/baths/sqft/year: {{beds}} / {{baths}} / {{sqft}} / {{year_built}}
Garage: {{garage_type}}  Lot acres: {{lot_size_acres}}
Known motivation: {{motivation}}
Timeline: {{timeline}}
Walk-away ask: {{walk_away_ask}}
House summary: {{house_info_summary}}

Goals: confirm identity/authority, motivation (Kong “besides price”), timeline,
property facts, ballpark alignment, book next step / Scout path.
Never invent ARV or guarantees. Use FAQ knowledge when objecting about scam/realtor/wholesale.
```

Runtime dispatch: `POST http://127.0.0.1:8792/api/voice/dispatch/{lead_id}`  
Webhook: `https://firstpropertyinvestment.us/api/voice/alex-retell-webhook`

Required dyn vars (strings): `customer_name`, `property_address`, `crm_summary`, `lead_id`.
Web call: `POST /api/voice/web-call/{lead_id}` · preview `GET /api/voice/web-call/preview/{lead_id}`.

## Retell flow dyn vars (authoritative)
- `{{customer.name}}` → key `customer.name` (Greeting)
- `{{first_name}}` / `{{last_name}}` → Confirm Name + crm_upsert_lead
- `{{lead_id}}` → tools (lookup/upsert/calendar/suppress/log)
- Phone is **not** a prompt placeholder. Dial via top-level `to_number` on create-phone-call.
- CRM phone field is `phone_primary` written by tools, not inbound `{{phone}}`.
- Do not send redundant `customer_phone` / `phone` / `phone_number` / dyn `to_number` aliases.

