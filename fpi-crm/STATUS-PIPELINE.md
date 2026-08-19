# FPI CRM pipeline statuses (locked v3)

| Code | Label (UI) | Who owns | What happened |
|------|------------|----------|----------------|
| `NEW_LISA_LEAD` | New Lisa Lead | Lisa | Ad found; SMS/email marketing + website link |
| `APPROVED_LEAD_SENDING_ALEX` | Approved lead → sending Alex | Website / chatbot | Opt-in on site; AI-call consent; phone + time window |
| `CURR_ALEX` | Curr Alex | Alex | Alex calling/texting; qualify in progress |
| `SCOUTING_LEAD` | Scouting Lead | Scout | Qualified **Y**; comps/rehab/MAO running |
| `WAITING_MAX_PRICE_SHANE` | Waiting Max Price (SHANE) | Shane | Scout done; need your max_price |
| `ALEX_MANAGING` | Alex managing | Alex | Max set; multi-day manage toward agreement |
| `CLIENT_APPROVED_CONTRACT_PENDING` | Client approved — contract pending | Alex/Ryan | Verbal/written yes; contract out |
| `CONTRACT_SIGNED` | Contract signed | Alex/Ryan | Signed + delivered |
| `FINDING_FLIPPER` | Finding flipper | **Blake** | Dispo / cash-buyer outreach |
| `ASSIGNED_TO_FLIPPER` | Assigned to flipper | Blake/Shane | Buyer under assignment |
| `CLOSED` | Closed | Shane | Done |
| `SUPPRESSED` | Suppressed / DNC | any | STOP |
| `DISQUALIFIED` | Disqualified | Alex/Scout | Fail qualify / buy box |
| `DEAD` | Dead | any | Dead file |
| `NURTURE` | Nurture | Lisa/Alex | Not now |

## Required field

- **`qualified`**: `Y` | `N` | null  
  - Set by Alex before leaving `CURR_ALEX`  
  - Only `Y` may go to `SCOUTING_LEAD`

## Happy path

```
Lisa (NEW_LISA_LEAD)
  → marketing email/SMS + http://firstpropertyinvestment.us/
  → seller hits site / chatbot, opts in + AI disclaimer consent
APPROVED_LEAD_SENDING_ALEX
  → Alex calls
CURR_ALEX → qualified=Y
SCOUTING_LEAD
WAITING_MAX_PRICE_SHANE  ← you set max_price
ALEX_MANAGING
CLIENT_APPROVED_CONTRACT_PENDING
CONTRACT_SIGNED
FINDING_FLIPPER (Blake)
ASSIGNED_TO_FLIPPER → CLOSED
```

## Website rules

- Chatbot answers FAQs + captures phone/name/address
- Scheduling: short call now OR pick callback window
- Clear **AI agent call disclaimer** before consent
- Consent text stored on lead (`ai_call_consent*`)

## Lisa to Alex
POST /api/voice/lisa/handoff/{lead_id} after checklist. Status APPROVED_LEAD_SENDING_ALEX then CURR_ALEX.
