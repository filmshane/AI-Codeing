# Morgan — local business receptionist

Desk voice loop + ElevenLabs Conversational AI agent.
Plan: `/opt/voice-receptionist/receptionist.plan`

## What this is
Morgan answers a business phone: hours, routing, messages, callbacks.
Not FPI Alex. Not a closer.

## Loops
- Phone: ElevenLabs ConvAI (Scribe realtime + Flash TTS) + dedicated Twilio number later
- Desk: `POST /api/loop/turn` → Scribe STT → Grok `:8645` → ElevenLabs TTS

## Run
```
sudo systemctl status voice-receptionist
curl -sS http://127.0.0.1:8793/api/health
```

Desk UI is `/` on 127.0.0.1:8793.

## Do not
- Reassign +14233801566
- PATCH agent_3101kzw4yn2fehvtcdn131x9yj56
- Live-dial without Shane’s test number
- Move WWW HTML
