#!/usr/bin/env python3
"""Migrate FPI CRM to v3.1 house-detail fields (Alex pre-Scout collection)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "fpi_crm.db"

COLS = {
    "phone_primary": "TEXT",
    "email_primary": "TEXT",
    "garage_type": "TEXT",  # none|detached|attached|carport|unknown
    "garage_spaces": "REAL",
    "lot_size_acres": "REAL",
    "lot_size_sqft": "REAL",
    "stories": "REAL",
    "basement_type": "TEXT",  # none|unfinished|partial|finished|unknown
    "last_remodel_year": "INTEGER",
    "last_remodel_notes": "TEXT",
    "roof_age_or_condition": "TEXT",
    "hvac_age_or_condition": "TEXT",
    "major_repairs_needed": "TEXT",
    "hoa": "TEXT",
    "pool": "TEXT",
    "tenant_lease_end": "TEXT",
    "listed_with_agent": "TEXT",  # Y|N|unknown
    "other_offers": "TEXT",
    "house_info_summary": "TEXT",
}


def main() -> None:
    if not DB.exists():
        raise SystemExit(f"No DB {DB}; run init_crm.py first")
    con = sqlite3.connect(DB)
    existing = {r[1] for r in con.execute("PRAGMA table_info(leads)")}
    for col, typ in COLS.items():
        if col not in existing:
            con.execute(f"ALTER TABLE leads ADD COLUMN {col} {typ}")
            print("added", col)
        else:
            print("exists", col)
    # backfill primary phone/email from json if empty
    rows = con.execute(
        "SELECT id, phones_json, emails_json, phone_primary, email_primary FROM leads"
    ).fetchall()
    import json

    for lid, pj, ej, pp, ep in rows:
        try:
            phones = json.loads(pj or "[]")
        except Exception:
            phones = []
        try:
            emails = json.loads(ej or "[]")
        except Exception:
            emails = []
        if not pp and phones:
            con.execute("UPDATE leads SET phone_primary=? WHERE id=?", (phones[0], lid))
        if not ep and emails:
            con.execute("UPDATE leads SET email_primary=? WHERE id=?", (emails[0], lid))

    # enrich demo lead house fields
    con.execute(
        """
        UPDATE leads SET
          garage_type = COALESCE(NULLIF(garage_type,''), 'attached'),
          garage_spaces = COALESCE(garage_spaces, 2),
          lot_size_acres = COALESCE(lot_size_acres, 0.46),
          lot_size_sqft = COALESCE(lot_size_sqft, 20038),
          stories = COALESCE(stories, 1),
          basement_type = COALESCE(NULLIF(basement_type,''), 'unfinished'),
          last_remodel_year = COALESCE(last_remodel_year, 2022),
          last_remodel_notes = COALESCE(NULLIF(last_remodel_notes,''),
            'Prior listing (2022) noted updated baths/kitchen; current remodel recency confirm with owner'),
          roof_age_or_condition = COALESCE(NULLIF(roof_age_or_condition,''), 'seller reports new/good'),
          hvac_age_or_condition = COALESCE(NULLIF(hvac_age_or_condition,''), 'unknown — Alex to confirm'),
          major_repairs_needed = COALESCE(NULLIF(major_repairs_needed,''),
            'Basement finish (floor/walls/ceiling/pipe conceal); kitchen gut; floors upstairs except sunroom+3 beds'),
          hoa = COALESCE(NULLIF(hoa,''), 'N'),
          pool = COALESCE(NULLIF(pool,''), 'N'),
          listed_with_agent = COALESCE(NULLIF(listed_with_agent,''), 'N'),
          house_info_summary = COALESCE(NULLIF(house_info_summary,''),
            '1965 brick ranch 4/3 2688sf, unfinished basement, 2-car attached, 0.46ac corner lot'),
          phone_primary = COALESCE(phone_primary, '+14235550151'),
          email_primary = COALESCE(email_primary, 'demo.seller@example.com'),
          first_name = COALESCE(first_name, 'Demo'),
          last_name = COALESCE(last_name, 'Seller')
        WHERE id LIKE '%1513%' OR property_address LIKE '%1513 18th%'
        """
    )
    con.execute(
        "INSERT OR REPLACE INTO schema_meta(key,value) VALUES ('version','3.1')"
    )
    con.commit()
    con.close()
    print("migrated", DB)


if __name__ == "__main__":
    main()
