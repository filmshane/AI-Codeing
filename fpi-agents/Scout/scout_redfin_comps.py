#!/usr/bin/env python3
"""Scout helper: Redfin subject + city sold-filter comps → rough package fields.
Usage:
  python3 scout_redfin_comps.py "1513 18th St NW" Cleveland TN 37311 \\
    --redfin-url https://www.redfin.com/TN/Cleveland/1513-18th-St-NW-37311/home/115039089 \\
    --city-id 3988 --beds 4 --sqft 2688
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics as st
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def fetch(url: str, referer: str = "https://www.redfin.com/") -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "text/html,*/*", "Referer": referer}
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def haversine(lat1, lon1, lat2, lon2) -> float:
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def parse_comps(html: str, slat: float, slon: float) -> list[dict]:
    text = html.replace('\\"', '"').replace("\\u002F", "/")
    parts = re.split(r'"propertyId":', text)
    comps = []
    for part in parts[1:]:
        chunk = part[:3000]
        m = re.match(r"(\d+)", chunk)
        if not m:
            continue

        def g(pat, cast=None):
            mm = re.search(pat, chunk)
            if not mm:
                return None
            return cast(mm.group(1)) if cast else mm.group(1)

        street = g(r'"streetLine":\{"value":"([^"]+)"')
        city = g(r'"city":"([^"]+)"')
        state = g(r'"state":"([^"]+)"')
        zipc = g(r'"zip":"([^"]+)"')
        price = g(r'"price":\{"value":(\d+)', int)
        beds = g(r'"beds":(\d+)', int)
        baths = g(r'"baths":([0-9.]+)', float)
        sqft = g(r'"sqFt":\{"value":(\d+)', int)
        year = g(r'"yearBuilt":\{"value":(\d+)', int)
        sold = g(r'"soldDate":(\d+)', int)
        lat = g(r'"latitude":([0-9.-]+)', float)
        lon = g(r'"longitude":([0-9.-]+)', float)
        url = g(r'"url":"([^"]+)"')
        ppsf = g(r'"pricePerSqFt":\{"value":(\d+)', int)
        if not (street and price and sold and state == "TN"):
            continue
        sds = datetime.fromtimestamp(sold / 1000, tz=timezone.utc).date().isoformat()
        dist = haversine(slat, slon, lat, lon) if lat and lon else None
        comps.append(
            {
                "property_id": int(m.group(1)),
                "address": f"{street}, {city}, {state} {zipc}",
                "sold_price": price,
                "sold_date": sds,
                "beds": beds,
                "baths": baths,
                "sqft": sqft,
                "year_built": year,
                "ppsf": ppsf or (round(price / sqft) if sqft else None),
                "distance_mi": round(dist, 2) if dist is not None else None,
                "url": ("https://www.redfin.com" + url)
                if url and str(url).startswith("/")
                else url,
                "lat": lat,
                "lon": lon,
            }
        )
    # dedupe
    seen, uniq = set(), []
    for c in comps:
        k = (c["address"], c["sold_price"], c["sold_date"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(c)
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("street")
    ap.add_argument("city")
    ap.add_argument("state")
    ap.add_argument("zipcode")
    ap.add_argument("--redfin-url", required=True)
    ap.add_argument("--city-id", required=True, help="Redfin city id, e.g. 3988 Cleveland TN")
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--beds", type=int, default=3)
    ap.add_argument("--sqft", type=int, required=True)
    ap.add_argument("--out", type=Path, default=Path("scout-comps-out.json"))
    args = ap.parse_args()

    subject_html = fetch(args.redfin_url)
    est = None
    m = re.search(r"id=\"redfin-estimate\".*?\$([0-9,]+)", subject_html, re.S)
    if m:
        est = int(m.group(1).replace(",", ""))
    if est is None:
        m = re.search(r"([0-9]{2,3},[0-9]{3})\s*Redfin Estimate|Redfin Estimate.*?([0-9]{2,3},[0-9]{3})", subject_html, re.S)
        # fallback already handled in prior runs via trafilatura

    sold_url = (
        f"https://www.redfin.com/city/{args.city_id}/{args.state}/{args.city}"
        f"/filter/property-type=house,include=sold-2yr,min-beds=3,min-sqft=1600,max-sqft=4000"
    )
    sold_html = fetch(sold_url, referer=f"https://www.redfin.com/city/{args.city_id}/{args.state}/{args.city}")
    comps = parse_comps(sold_html, args.lat, args.lon)
    band = [
        c
        for c in comps
        if c.get("distance_mi") is not None
        and c["distance_mi"] <= 3
        and c.get("sqft")
        and 0.65 * args.sqft <= c["sqft"] <= 1.35 * args.sqft
        and args.street.split()[0] not in c["address"]
    ]
    band = sorted(band, key=lambda c: (c["distance_mi"], c["sold_date"]))
    payload = {
        "subject": {
            "address": f"{args.street}, {args.city}, {args.state} {args.zipcode}",
            "redfin_url": args.redfin_url,
            "lat": args.lat,
            "lon": args.lon,
            "beds_hint": args.beds,
            "sqft": args.sqft,
            "redfin_estimate_usd": est,
        },
        "sold_filter_url": sold_url,
        "comps_parsed": len(comps),
        "comps_band": band[:25],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if band:
        prices = [c["sold_price"] for c in band[:15]]
        ppsf = [c["ppsf"] for c in band[:15] if c.get("ppsf")]
        payload["stats"] = {
            "median_price": st.median(prices),
            "median_ppsf": st.median(ppsf) if ppsf else None,
            "arv_ppsf_x_gla": round(st.median(ppsf) * args.sqft) if ppsf else None,
        }
    args.out.write_text(json.dumps(payload, indent=2))
    print(json.dumps({"wrote": str(args.out), "comps_band": len(band), "estimate": est}, indent=2))


if __name__ == "__main__":
    main()
