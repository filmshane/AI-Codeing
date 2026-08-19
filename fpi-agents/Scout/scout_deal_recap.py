#!/usr/bin/env python3
"""Build Scout DEAL RECAP block (JSON + markdown footer)."""
from __future__ import annotations

from typing import Any


def build_deal_recap(
    arv: float,
    rehab: float,
    *,
    case_name: str = "medium_rehab",
    assignment_fee: float = 15_000,
    arv_factor: float = 0.70,
    buy_closing_pct: float = 0.02,
    sell_closing_pct: float = 0.07,
    hold_reserve: float = 8_000,
    buyer_cushion_safe: float = 10_000,
    open_under_max_high: float = 10_000,
    open_under_max_low: float = 15_000,
) -> dict[str, Any]:
    arv = float(arv)
    rehab = float(rehab)
    mao_flip = round(arv * arv_factor - rehab)
    you_lock = mao_flip - round(assignment_fee)
    flipper_all_in = mao_flip
    buy_closing = round(flipper_all_in * buy_closing_pct)
    sell_closing = round(arv * sell_closing_pct)
    total = flipper_all_in + buy_closing + round(rehab) + round(hold_reserve) + sell_closing
    profit = round(arv - total)
    margin = round(profit / arv, 3) if arv else 0.0
    safer = you_lock - round(buyer_cushion_safe)
    open_high = max(0, you_lock - round(open_under_max_high))
    open_low = max(0, you_lock - round(open_under_max_low))
    fee = round(assignment_fee)

    if you_lock <= 0 or profit <= 0:
        verdict = (
            f"No: stack does not work at this ARV/rehab/fee "
            f"(seller max ${you_lock:,.0f}, flipper profit ${profit:,.0f}). Pass or re-scope."
        )
        works = False
    elif profit < 20_000:
        verdict = (
            f"Thin: you ${fee:,.0f} leaves flipper only ~${profit:,.0f}. "
            "Cut seller price, cut fee, or pass."
        )
        works = False
    elif profit < 50_000:
        verdict = (
            f"Marginal: you ${fee:,.0f} works only if ARV/rehab stay tight; "
            f"prefer safer lock ~${max(0,safer):,.0f} or confirm bids."
        )
        works = True
    else:
        verdict = (
            f"So yes: you ${fee:,.0f}, flipper still has solid meat (~${profit:,.0f}) "
            "if ARV and rehab hold. (Healthy.)"
        )
        works = True

    md = f"""---

## DEAL RECAP (default case: {case_name})

### Roles / stack

| Role | Number |
|------|--------:|
| You lock seller at (max) | ${you_lock:,.0f} |
| Your fee | ${fee:,.0f} |
| Flipper all-in | ${flipper_all_in:,.0f} |
| Flipper rehab | ${rehab:,.0f} |
| Flipper sells (ARV) | ${arv:,.0f} |

**Open range (negotiate under max):** ${open_low:,.0f} – ${open_high:,.0f}  
**Safer lock (extra ${buyer_cushion_safe:,.0f} buyer meat):** ${safer:,.0f}

### Step 3 — Does the flipper still make money?

Rough flip P&L if they buy at flipper all-in, complete rehab, sell at ARV:

| | |
|--|--:|
| Purchase | ${flipper_all_in:,.0f} |
| Buy closing ~{buy_closing_pct:.0%} | ${buy_closing:,.0f} |
| Rehab | ${rehab:,.0f} |
| Hold (taxes/ins/util/loan) | ${hold_reserve:,.0f} |
| Sell costs ~{sell_closing_pct:.0%} (commission+closing) | ${sell_closing:,.0f} |
| **Total project cost** | **${total:,.0f}** |
| **ARV sale** | **${arv:,.0f}** |
| **Flipper profit** | **${profit:,.0f}** |

### Verdict

{verdict}

- 70% rule is the screen (`MAO_flip = ARV×{arv_factor:.2f} − rehab`).
- Full stack above shows flipper profit at MAO (~{margin:.1%} of ARV).
- Shane sets `max_price` ≤ you-lock-seller-max (or safer lock). Ryan never exceeds max_price.
"""

    return {
        "case_name": case_name,
        "arv": round(arv),
        "rehab": round(rehab),
        "arv_factor": arv_factor,
        "mao_flip": mao_flip,
        "assignment_fee": fee,
        "you_lock_seller_max": you_lock,
        "flipper_all_in": flipper_all_in,
        "open_low": open_low,
        "open_high": open_high,
        "safer_seller_lock": safer,
        "buyer_cushion_safe": round(buyer_cushion_safe),
        "buy_closing_pct": buy_closing_pct,
        "sell_closing_pct": sell_closing_pct,
        "hold_reserve": round(hold_reserve),
        "buy_closing": buy_closing,
        "sell_closing": sell_closing,
        "total_project_cost": total,
        "flipper_profit": profit,
        "flipper_margin_on_arv": margin,
        "works": works,
        "verdict": verdict,
        "markdown_footer": md,
    }


if __name__ == "__main__":
    import json
    import sys

    arv = float(sys.argv[1]) if len(sys.argv) > 1 else 429_000
    rehab = float(sys.argv[2]) if len(sys.argv) > 2 else 120_000
    r = build_deal_recap(arv, rehab)
    print(r["markdown_footer"])
    print(json.dumps({k: v for k, v in r.items() if k != "markdown_footer"}, indent=2))
