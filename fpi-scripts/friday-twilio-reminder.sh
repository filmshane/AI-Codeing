#!/usr/bin/env bash
# One-shot Friday Twilio setup attention grabber
set -euo pipefail
SLOT="${1:-reminder}"
HOST="$(hostname -s 2>/dev/null || echo host)"
TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
MSG="FPI REMINDER ($SLOT) @ $TS on $HOST
========================================
Shane — set up TWILIO today (you said separately from Hermes).
Then fill out phone number + SIP info for ElevenLabs Alex outbound.

Next steps:
  1) Twilio console: phone number + SIP / trunk as needed
  2) Import/connect number in ElevenLabs ConvAI
  3) Give Mike: ELEVENLABS_AGENT_PHONE_NUMBER_ID (and confirm number)
  4) Mike wires /opt/fpi-voice/.env and verifies open-call

Agent: agent_3101kzw4yn2fehvtcdn131x9yj56
Webhook: already live (HMAC enforced)
API key: already set
Still missing: ELEVENLABS_AGENT_PHONE_NUMBER_ID
========================================"

# Broadcast to all terminals
printf '%s\n' "$MSG" | wall 2>/dev/null || true

# GNOME desktop notification (user session)
export DISPLAY="${DISPLAY:-:0}"
# Find shanem session bus if possible
if [[ -z "${DBUS_SESSION_BUS_ADDRESS:-}" ]]; then
  for b in /run/user/1000/bus; do
    [[ -S "$b" ]] && export DBUS_SESSION_BUS_ADDRESS="unix:path=$b" && break
  done
fi
if command -v notify-send >/dev/null 2>&1; then
  sudo -u shanem DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/1000/bus}" \
    notify-send -u critical -t 0 \
    "FPI: Twilio setup ($SLOT)" \
    "Set up Twilio, then phone number + SIP for ElevenLabs Alex outbound. Phone number id still missing." \
    2>/dev/null || \
  notify-send -u critical -t 0 \
    "FPI: Twilio setup ($SLOT)" \
    "Set up Twilio, then phone number + SIP for ElevenLabs Alex outbound." \
    2>/dev/null || true
fi

# Also write a sticky flag file on desktop/home if possible
FLAG="/home/shanem/TWILIO-SETUP-REMINDER-$SLOT.txt"
printf '%s\n' "$MSG" > "$FLAG"
chown shanem:shanem "$FLAG" 2>/dev/null || true

# Log
echo "[$TS] wall+notify Twilio reminder slot=$SLOT" >> /home/shanem/FPI-Corp/scripts/reminder.log
chown shanem:shanem /home/shanem/FPI-Corp/scripts/reminder.log 2>/dev/null || true
