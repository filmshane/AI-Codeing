#!/usr/bin/env python3
"""Print full-field CRM report for one lead or all leads."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "fpi_crm.db"

STATUS_LABELS = {
    "NEW_LISA_LEAD": "New Lisa Lead",
    "APPROVED_LEAD_SENDING_ALEX": "Approved lead → sending Alex",
    "CURR_ALEX": "Curr Alex (on phone/SMS with Alex)",
    "SCOUTING_LEAD": "Scouting Lead",
    "WAITING_MAX_PRICE_SHANE": "Waiting Max Price (SHANE)",
    "ALEX_MANAGING": "Alex managing",
    "CLIENT_APPROVED_CONTRACT_PENDING": "Client approved — contract pending",
    "CONTRACT_SIGNED": "Contract signed",
    "FINDING_FLIPPER": "Finding flipper / dispo",
    "ASSIGNED_TO_FLIPPER": "Assigned to flipper",
    "CLOSED": "Closed",
    "SUPPRESSED": "Suppressed / DNC",
    "DISQUALIFIED": "Disqualified",
    "DEAD": "Dead",
    "NURTURE": "Nurture",
}


def fmt(v):
    if v is None or v == "":
        return "—"
    return str(v)


def money(v):
    if v is None:
        return "—"
    try:
        return f"${float(v):,.0f}"
    except (TypeError, ValueError):
        return str(v)


def report_lead(con: sqlite3.Connection, lead_id: str | None = None) -> str:
    con.row_factory = sqlite3.Row
    if lead_id:
        rows = con.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchall()
    else:
        rows = con.execute("SELECT * FROM leads ORDER BY updated_at DESC").fetchall()
    if not rows:
        return "No leads found.\n"

    out = []
    out.append("=" * 72)
    out.append("FPI CRM REPORT — ALL FIELDS")
    out.append(f"Database: {DB}")
    out.append("=" * 72)

    # pipeline counts
    counts = con.execute(
        "SELECT status, COUNT(*) c FROM leads GROUP BY status ORDER BY c DESC"
    ).fetchall()
    out.append("\n## PIPELINE COUNTS (stage)")
    for r in counts:
        label = STATUS_LABELS.get(r["status"], r["status"])
        out.append(f"  {label:42} {r['c']}")

    for row in rows:
        d = dict(row)
        st = d.get("status")
        out.append("\n" + "#" * 72)
        out.append(f"LEAD ID: {d['id']}")
        out.append(f"STAGE:   {STATUS_LABELS.get(st, st)}  [{st}]")
        out.append(f"Owner agent: {fmt(d.get('owner_agent'))} | Stage entered: {fmt(d.get('stage_entered_at'))}")
        out.append(f"Updated: {fmt(d.get('updated_at'))} | Created: {fmt(d.get('created_at'))}")

        out.append("\n## CONTACT")
        out.append(f"  Name:        {fmt(d.get('full_name'))} ({fmt(d.get('first_name'))} {fmt(d.get('last_name'))})")
        out.append(f"  Phones:      {fmt(d.get('phones_json'))}")
        out.append(f"  Emails:      {fmt(d.get('emails_json'))}")
        out.append(f"  Preferred:   {fmt(d.get('preferred_contact'))} | Best time: {fmt(d.get('best_time_to_call'))}")
        out.append(f"  Timezone:    {fmt(d.get('timezone'))}")
        out.append(f"  DNC:         {bool(d.get('do_not_contact'))} {fmt(d.get('dnc_reason'))}")

        out.append("\n## PROPERTY")
        out.append(f"  Address:     {fmt(d.get('property_address'))}")
        out.append(f"  City/ST/Zip: {fmt(d.get('property_city'))}, {fmt(d.get('property_state'))} {fmt(d.get('property_zip'))}")
        out.append(f"  Lat/Lon:     {fmt(d.get('property_lat'))}, {fmt(d.get('property_lon'))}")
        out.append(f"  Type/beds/ba/sf/yr: {fmt(d.get('property_type'))} | {fmt(d.get('beds'))}/{fmt(d.get('baths'))} | {fmt(d.get('sqft'))} sf | {fmt(d.get('year_built'))}")
        out.append(f"  Occupancy:   {fmt(d.get('occupancy'))}")
        out.append(f"  Condition:   {fmt(d.get('condition_notes'))}")

        out.append("\n## LISA / SOURCE")
        out.append(f"  Platform:    {fmt(d.get('source_platform'))}")
        out.append(f"  Ad URL:      {fmt(d.get('source_ad_url'))}")
        out.append(f"  Ad title:    {fmt(d.get('source_ad_title'))}")
        out.append(f"  Ask:         {money(d.get('source_price_ask'))}")
        out.append(f"  Email sent:  {fmt(d.get('marketing_email_sent_at'))}")
        out.append(f"  SMS sent:    {fmt(d.get('marketing_sms_sent_at'))}")
        out.append(f"  Site link:   {fmt(d.get('website_link_sent_at'))}")
        out.append(f"  Lisa notes:  {fmt(d.get('lisa_notes'))}")

        out.append("\n## WEBSITE / OPT-IN / AI CONSENT")
        out.append(f"  Website hit: {fmt(d.get('website_hit_at'))}")
        out.append(f"  Opt-in:      {bool(d.get('website_opt_in'))} @ {fmt(d.get('website_opt_in_at'))}")
        out.append(f"  AI consent:  {bool(d.get('ai_call_consent'))} @ {fmt(d.get('ai_call_consent_at'))}")
        out.append(f"  Consent txt: {fmt(d.get('ai_call_consent_text'))}")
        out.append(f"  Call window: {fmt(d.get('preferred_call_window'))} | short_call={bool(d.get('available_for_short_call'))}")

        out.append("\n## ALEX / QUALIFY")
        out.append(f"  QUALIFIED:   {fmt(d.get('qualified'))}  (Y/N) @ {fmt(d.get('qualified_at'))} by {fmt(d.get('qualified_by'))}")
        out.append(f"  Motivation:  {fmt(d.get('motivation'))}")
        out.append(f"  Detail:      {fmt(d.get('motivation_detail'))}")
        out.append(f"  Timeline:    {fmt(d.get('timeline'))}")
        out.append(f"  Walk-away:   {money(d.get('walk_away_ask'))}")
        out.append(f"  Mortgage ~:  {money(d.get('mortgage_balance_approx'))}")
        out.append(f"  Authority:   {fmt(d.get('owner_authority_notes'))}")
        out.append(f"  Appointment: {fmt(d.get('appointment_at'))}")
        out.append(f"  Alex notes:  {fmt(d.get('alex_notes'))}")

        out.append("\n## SCOUT NUMBERS")
        out.append(f"  Scout status:{fmt(d.get('scout_status'))}")
        out.append(f"  Package:     {fmt(d.get('scout_package_path'))}")
        out.append(f"  ARV L/W/H:   {money(d.get('scout_arv_low'))} / {money(d.get('scout_arv_working'))} / {money(d.get('scout_arv_high'))}")
        out.append(f"  Rehab L/M/H: {money(d.get('scout_rehab_low'))} / {money(d.get('scout_rehab_medium'))} / {money(d.get('scout_rehab_high'))}")
        out.append(f"  MAO flip L/M/H: {money(d.get('scout_mao_flip_low'))} / {money(d.get('scout_mao_flip_medium'))} / {money(d.get('scout_mao_flip_high'))}")
        out.append(f"  Seller max L/M/H (after fee): {money(d.get('scout_seller_max_low'))} / {money(d.get('scout_seller_max_medium'))} / {money(d.get('scout_seller_max_high'))}")
        out.append(f"  Assignment fee target: {money(d.get('scout_assignment_fee'))}")
        out.append(f"  Deal works (med): {bool(d.get('scout_deal_works_medium'))}")

        out.append("\n## SHANE MAX PRICE")
        out.append(f"  max_price:   {money(d.get('max_price'))}")
        out.append(f"  set at/by:   {fmt(d.get('max_price_set_at'))} / {fmt(d.get('max_price_set_by'))}")
        out.append(f"  case:        {fmt(d.get('underwriting_case'))}")

        out.append("\n## CONTRACT")
        out.append(f"  status:      {fmt(d.get('contract_status'))}")
        out.append(f"  client appr: {fmt(d.get('client_approved_contract_at'))}")
        out.append(f"  sent/signed: {fmt(d.get('contract_sent_at'))} / {fmt(d.get('contract_signed_at'))}")
        out.append(f"  28h remind:  {fmt(d.get('contract_reminder_28h_at'))}")

        out.append("\n## FLIPPER / DISPO")
        out.append(f"  flipper st:  {fmt(d.get('flipper_status'))}")
        out.append(f"  target $:    {money(d.get('flipper_target_price'))}")
        out.append(f"  assigned:    {fmt(d.get('assigned_flipper_name'))} ({fmt(d.get('assigned_flipper_id'))})")
        out.append(f"  fee actual:  {money(d.get('assignment_fee_actual'))}")

        out.append("\n## NOTES / UTM")
        out.append(f"  utm:         {fmt(d.get('utm_campaign'))}")
        out.append(f"  notes:       {fmt(d.get('notes'))}")

        # history
        hist = con.execute(
            "SELECT from_status, to_status, actor, at, note FROM status_history WHERE lead_id=? ORDER BY at",
            (d["id"],),
        ).fetchall()
        out.append("\n## STATUS HISTORY")
        if not hist:
            out.append("  (none)")
        for h in hist:
            out.append(
                f"  {h['at'][:19]}  {fmt(h['from_status'])} → {h['to_status']}  [{h['actor']}] {fmt(h['note'])}"
            )

        acts = con.execute(
            "SELECT at, actor, type, payload_json FROM activities WHERE lead_id=? ORDER BY at DESC LIMIT 15",
            (d["id"],),
        ).fetchall()
        out.append("\n## RECENT ACTIVITIES")
        for a in acts:
            out.append(f"  {a['at'][:19]}  {a['actor']:8}  {a['type']:28}  {fmt(a['payload_json'])[:80]}")

        # practical strip for waiting max
        if st == "WAITING_MAX_PRICE_SHANE":
            out.append("\n## PRACTICAL (this stage)")
            out.append(f"  Set max_price ≤ seller max medium {money(d.get('scout_seller_max_medium'))}")
            out.append(f"  Default underwriting: {fmt(d.get('underwriting_case'))}")
            out.append("  Next status after max set: ALEX_MANAGING (then contract path)")

    out.append("\n" + "=" * 72)
    out.append("END CRM REPORT")
    out.append("=" * 72 + "\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lead", help="Lead id (default: all)")
    ap.add_argument("-o", "--out", type=Path, help="Write report to file")
    args = ap.parse_args()
    if not DB.exists():
        raise SystemExit(f"No DB at {DB}. Run init_crm.py first.")
    con = sqlite3.connect(DB)
    text = report_lead(con, args.lead)
    con.close()
    if args.out:
        args.out.write_text(text)
        print(f"Wrote {args.out}")
    print(text)


if __name__ == "__main__":
    main()
