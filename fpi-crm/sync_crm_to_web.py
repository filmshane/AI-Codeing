#!/usr/bin/env python3
"""Sync project CRM SQLite to web-readable copy under /var/www/.../CRM/data/"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

SRC = Path(__file__).resolve().parent / "fpi_crm.db"
DEST_DIR = Path("/var/www/firstpropertyinvestment.us/CRM/data")
DEST = DEST_DIR / "fpi_crm.db"


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing {SRC}")
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    # consistent snapshot
    tmp = DEST.with_suffix(".db.tmp")
    shutil.copy2(SRC, tmp)
    tmp.replace(DEST)
    subprocess.run(
        ["chown", "www-data:www-data", str(DEST), str(DEST_DIR)],
        check=False,
    )
    subprocess.run(["chmod", "640", str(DEST)], check=False)
    subprocess.run(["chmod", "750", str(DEST_DIR)], check=False)
    print(f"synced {SRC} → {DEST}")


if __name__ == "__main__":
    main()
