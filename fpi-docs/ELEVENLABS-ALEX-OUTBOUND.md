# ElevenLabs + Alex outbound (FPI)

Sources: ElevenLabs ElevenAgents docs (post-call webhooks, Twilio outbound, personalization, pricing/agents). Prices change — re-check https://elevenlabs.io/pricing/agents

## Important: what “activates” the call

**Alex does not start a phone call via a webhook FROM ElevenLabs.**

Your side (CRM / Lisa handoff / website opt-in) **calls ElevenLabs** to place the outbound call.

| Direction | Mechanism |
|-----------|-----------|
| **Start outbound call** | Your server → `POST https://api.elevenlabs.io/v1/convai/twilio/outbound-call` |
| **During call (CRM tools)** | Alex agent → **webhook tools** → your HTTPS APIs |
| **Inbound personalization** (if they call you) | ElevenLabs → your **conversation initiation webhook** |
| **After call** | ElevenLabs → your **post-call webhooks** |

---

## 1) What you need on FPI side

### A. ElevenLabs account setup
1. Create **Alex** agent (system prompt from `/home/shanem/FPI-Corp/Alex/alex-lead-manager.system.md`).
2. Attach **Knowledge base** / RAG if desired (FAQ can also be webhook tools into Chroma).
3. Import **Twilio** number (or verified caller ID for outbound-only).
4. API key: `xi-api-key`.

### B. Your API (HTTPS, public)
Recommended endpoints under something like `https://api.yourdomain/...` or a tunnel for lab:

| Endpoint | Who calls it | Purpose |
|----------|--------------|---------|
| `POST /fpi/alex/outbound` | Lisa / CRM / website | **Your** trigger → calls ElevenLabs outbound-call |
| `POST /fpi/webhooks/elevenlabs/post-call` | ElevenLabs | Transcript, analysis, audio → update CRM |
| `POST /fpi/webhooks/elevenlabs/call-failed` | ElevenLabs | `call_initiation_failure` |
| `POST /fpi/webhooks/elevenlabs/personalization` | ElevenLabs (inbound only) | Return dynamic vars + prompt overrides |
| Webhook **tools** e.g. `/fpi/tools/crm_lookup`, `crm_upsert`, `retrieve_seller_faq`, `calendar_book` | Alex mid-call | CRM + FAQ |

**Must:**
- HTTPS
- Return **HTTP 200** on post-call webhooks (10 consecutive failures → auto-disable)
- Verify **`ElevenLabs-Signature`** HMAC (`construct_event` / `constructEvent`)
- Store webhook secret from Agents settings
- Optional: allowlist ElevenLabs egress IPs

### C. Outbound call request (activate Alex)

```http
POST https://api.elevenlabs.io/v1/convai/twilio/outbound-call
xi-api-key: YOUR_KEY
Content-Type: application/json

{
  "agent_id": "agent_xxx",
  "agent_phone_number_id": "phnum_xxx",
  "to_number": "+1...",
  "conversation_initiation_client_data": {
    "dynamic_variables": {
      "first_name": "Jane",
      "property_address": "1513 18th St NW...",
      "lead_id": "lead-...",
      "preferred_window": "weekday mornings"
    },
    "conversation_config_override": {
      "agent": {
        "first_message": "Hi Jane, this is Alex with First Property Investment..."
      }
    }
  }
}
```

Required body fields: `agent_id`, `agent_phone_number_id`, `to_number`.

Batch alternative: Batch Calling UI/API (CSV + `phone_number` column) — still **your** campaign, not a webhook inbound.

### D. Post-call webhooks (workspace Agents settings)

Types:
1. **`post_call_transcription`** — full transcript + analysis (primary for CRM)
2. **`post_call_audio`** — base64 audio (optional)
3. **`call_initiation_failure`** — no-answer / fail reasons

Use these to set CRM: `CURR_ALEX` → qualified Y/N → `SCOUTING_LEAD` etc.

### E. Twilio personalization webhook (inbound only)

If someone calls your FPI number, ElevenLabs POSTs:
`caller_id`, `agent_id`, `called_number`, `call_sid`

You return:
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": { "...": "..." },
  "conversation_config_override": { "agent": { "first_message": "..." } }
}
```

Not required to **start** Alex outbound after website YES.

### F. Compliance
- TCPA / consent recorded (website AI disclosure + opt-in already on FPI site)
- DNC checks before outbound
- Honest AI disclosure on the call (in Alex prompt)

---

## 2) Minimal Alex activation flow (FPI)

```
Website / Lisa: YES + phone + AI consent
        ↓
CRM: APPROVED_LEAD_SENDING_ALEX
        ↓
YOUR server POST /fpi/alex/outbound
        ↓
ElevenLabs POST .../twilio/outbound-call
        ↓
Call rings → Alex agent talks
        ↓
Mid-call: webhook tools → CRM/FAQ
        ↓
End: post_call_transcription → CRM update (qualified Y/N, notes)
```

---

## 3) Prices (ElevenAgents — as of docs check 2026-08)

From https://elevenlabs.io/pricing/agents (monthly; taxes extra):

| Plan | Monthly | Included call minutes | Concurrent calls |
|------|--------:|----------------------:|-----------------:|
| Free | $0 | 15 | 4 |
| Starter | $6 | 75 | 6 |
| Creator | $22 (first mo $11) | 275 | 10 |
| Pro | $99 | 1,238 | 20 |
| Scale | $299 | 3,738 | 30 |
| Business | $990 | 12,375 | 40 |
| Enterprise | Custom | Custom | Elevated |

**Usage beyond included (ElevenLabs hosting):**
- Additional call: **~$0.08 / minute**
- Burst (over concurrency): **~$0.16 / minute**
- Text message: **~$0.003 / message**

**Extra (not in that $0.08 alone):**
- **LLM** — billed separately by model (from ElevenLabs credits / pass-through)
- **Twilio telephony** — your Twilio account (per-minute + number)

Rough lab budget: Creator ($22) + Twilio number + ~$0.08/min overage + LLM is a common start; Pro if concurrent outbound ramps.

---

## 4) Docs links

- Outbound: https://elevenlabs.io/docs/api-reference/twilio/outbound-call
- Post-call webhooks: https://elevenlabs.io/docs/eleven-agents/workflows/post-call-webhooks
- Twilio personalization: https://elevenlabs.io/docs/eleven-agents/customization/personalization/twilio-personalization
- Webhook tools: https://elevenlabs.io/docs/eleven-agents/customization/tools/webhook-tools
- Batch calls: https://elevenlabs.io/docs/eleven-agents/phone-numbers/batch-calls
- Pricing: https://elevenlabs.io/pricing/agents

## Live webhook URL
`https://firstpropertyinvestment.us/api/voice/alex-elevenlabs-webhook`
See `ELEVENLABS-WEBHOOK.md`.
