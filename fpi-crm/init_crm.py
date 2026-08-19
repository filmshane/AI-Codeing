#!/usr/bin/env python3
"""Initialize FPI CRM v3 and seed demo lead 1513 18th St NW (Waiting Max Price)."""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "fpi_crm.db"
SCHEMA = ROOT / "schema.sql"
PKG = Path("/home/shanem/FPI-Corp/Docs/scout-runs/scout-package-1513-18th-st-nw-cleveland-tn.json")

STATUSES = [
    "NEW_LISA_LEAD",
    "APPROVED_LEAD_SENDING_ALEX",
    "CURR_ALEX",
    "SCOUTING_LEAD",
    "WAITING_MAX_PRICE_SHANE",
    "ALEX_MANAGING",
    "CLIENT_APPROVED_CONTRACT_PENDING",
    "CONTRACT_SIGNED",
    "FINDING_FLIPPER",
    "ASSIGNED_TO_FLIPPER",
    "CLOSED",
    "SUPPRESSED",
    "DISQUALIFIED",
    "DEAD",
    "NURTURE",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def main() -> int:
    if DB.exists():
        bak = ROOT / f"fpi_crm.db.bak-{datetime.now().strftime('%Y%m%d-%H%M')}"
        shutil.copy2(DB, bak)
        print(f"backed up → {bak}")
        DB.unlink()

    con = sqlite3.connect(DB)
    con.executescript(SCHEMA.read_text())
    ts = now()

    pkg = {}
    if PKG.exists():
        pkg = json.loads(PKG.read_text())

    arv = pkg.get("arv_working") or 429000
    rehab = (pkg.get("rehab") or {})
    # prefer deal_recap_by_tier if present
    by = pkg.get("deal_recap_by_tier") or {}
    def tier_rehab(name, fallback):
        if name in by and by[name].get("rehab"):
            return by[name]["rehab"]
        return fallback

    r_low = tier_rehab("low", (rehab.get("low") or {}).get("estimate_usd") or 63043)
    r_med = tier_rehab("medium", (rehab.get("medium") or {}).get("estimate_usd") or 119582)
    r_high = tier_rehab("high", (rehab.get("full_gut") or rehab.get("high") or {}).get("estimate_usd") or 209722)

    fee = 15000
    def mao(r):
        return round(arv * 0.70 - r)

    lead_id = "lead-1513-18th-st-nw-cleveland"
    status = "WAITING_MAX_PRICE_SHANE"

    con.execute(
        """
        INSERT INTO leads (
          id, full_name, first_name, last_name, phones_json, emails_json,
          preferred_contact, best_time_to_call, timezone,
          property_address, property_city, property_state, property_zip,
          property_lat, property_lon, property_type, beds, baths, sqft, year_built,
          occupancy, condition_notes,
          source_platform, source_ad_url, lisa_notes,
          marketing_email_sent_at, marketing_sms_sent_at, website_link_sent_at,
          website_hit_at, website_opt_in, website_opt_in_at,
          ai_call_consent, ai_call_consent_text, ai_call_consent_at,
          preferred_call_window, available_for_short_call,
          qualified, qualified_at, qualified_by,
          motivation, motivation_detail, timeline, walk_away_ask,
          owner_authority_notes, alex_notes, appointment_at,
          status, owner_agent, stage_entered_at,
          scout_status, scout_package_path,
          scout_arv_working, scout_arv_low, scout_arv_high,
          scout_rehab_low, scout_rehab_medium, scout_rehab_high,
          scout_mao_flip_low, scout_mao_flip_medium, scout_mao_flip_high,
          scout_seller_max_low, scout_seller_max_medium, scout_seller_max_high,
          scout_assignment_fee, scout_deal_works_medium, scout_recap_json,
          max_price, underwriting_case, notes, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            lead_id,
            "Demo Seller",
            "Demo",
            "Seller",
            json.dumps(["+14235550151"]),
            json.dumps(["demo.seller@example.com"]),
            "sms",
            "weekday mornings",
            "America/New_York",
            "1513 18th St NW, Cleveland, TN 37311",
            "Cleveland",
            "TN",
            "37311",
            35.1771304,
            -84.8867932,
            "SFR brick ranch",
            4,
            3.0,
            2688,
            1965,
            "unknown",
            "Basement finish needed; kitchen gut; floors partial; roof/paint/windows OK",
            "demo_seed",
            "https://www.redfin.com/TN/Cleveland/1513-18th-St-NW-37311/home/115039089",
            "Seeded from Scout package for CRM lock-in demo",
            ts,
            ts,
            ts,
            ts,
            1,
            ts,
            1,
            "Yes, an AI from First Property Investment may call me about selling my property.",
            ts,
            "short_call_now",
            1,
            "Y",
            ts,
            "alex",
            "tired landlord / as-is cash interest (demo)",
            "Demo motivation for pipeline walkthrough",
            "30-60 days",
            250000,
            "sole owner (demo)",
            "Qualified on demo call; booked scout; awaiting Shane max",
            None,
            status,
            "shane",
            ts,
            "done",
            str(PKG) if PKG.exists() else None,
            arv,
            pkg.get("arv_low") or 390000,
            pkg.get("arv_high") or 445000,
            r_low,
            r_med,
            r_high,
            mao(r_low),
            mao(r_med),
            mao(r_high),
            mao(r_low) - fee,
            mao(r_med) - fee,
            mao(r_high) - fee,
            fee,
            1,
            json.dumps(pkg.get("deal_recap_by_tier") or pkg.get("deal_recap") or {}),
            None,
            "medium",
            "CRM v3 seed — set max_price to advance past WAITING_MAX_PRICE_SHANE",
            ts,
            ts,
        ),
    )

    # status history path
    path = [
        (None, "NEW_LISA_LEAD", "lisa"),
        ("NEW_LISA_LEAD", "APPROVED_LEAD_SENDING_ALEX", "website"),
        ("APPROVED_LEAD_SENDING_ALEX", "CURR_ALEX", "alex"),
        ("CURR_ALEX", "SCOUTING_LEAD", "alex"),
        ("SCOUTING_LEAD", "WAITING_MAX_PRICE_SHANE", "scout"),
    ]
    for fr, to, actor in path:
        con.execute(
            "INSERT INTO status_history (id, lead_id, from_status, to_status, actor, at, note) VALUES (?,?,?,?,?,?,?)",
            (uid("sh-"), lead_id, fr, to, actor, ts, "seed pipeline"),
        )

    con.execute(
        "INSERT INTO activities (id, lead_id, actor, type, payload_json, at) VALUES (?,?,?,?,?,?)",
        (uid("act-"), lead_id, "system", "crm_v3_seeded", json.dumps({"status": status}), ts),
    )
    con.execute(
        "INSERT INTO activities (id, lead_id, actor, type, payload_json, at) VALUES (?,?,?,?,?,?)",
        (
            uid("act-"),
            lead_id,
            "scout",
            "scout_completed",
            json.dumps({"arv": arv, "rehab_medium": r_med, "seller_max_medium": mao(r_med) - fee}),
            ts,
        ),
    )

    if PKG.exists():
        con.execute(
            "INSERT INTO scout_runs (id, lead_id, package_json, package_path, status, created_at) VALUES (?,?,?,?,?,?)",
            (uid("run-"), lead_id, json.dumps(pkg), str(PKG), "done", ts),
        )

    # sample flipper targets (Blake seeds)
    for company, web, stype, repair in [
        (
            "Example Chattanooga Cash Buyers",
            "https://example-chatt-cash.local",
            "website",
            1,
        ),
        (
            "Example Cleveland Fix & Flip LLC",
            "https://example-cleveland-flip.local",
            "zillow_investor",
            1,
        ),
    ]:
        con.execute(
            """INSERT INTO flippers (id, company_name, website, markets_json, source_type, has_repair_arm, notes, last_researched_at, active, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,1,?,?)""",
            (
                uid("fl-"),
                company,
                web,
                json.dumps(["Chattanooga", "Cleveland TN"]),
                stype,
                repair,
                "Placeholder seed — replace with Blake live research",
                ts,
                ts,
                ts,
            ),
        )

    con.execute(
        "INSERT OR REPLACE INTO schema_meta(key,value) VALUES ('statuses_json', ?)",
        (json.dumps(STATUSES),),
    )
    con.commit()
    con.close()
    print(f"CRM ready: {DB}")
    print(f"lead {lead_id} status={status}")
    print("statuses:", ", ".join(STATUSES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
