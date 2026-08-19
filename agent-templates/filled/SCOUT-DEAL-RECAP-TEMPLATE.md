# Scout report — mandatory DEAL RECAP (footer)

Every Scout **markdown report** and every Scout **JSON package** MUST end with DEAL RECAP
for **all three rehab tiers: low, medium, high** (plus a side-by-side table), using:

Config defaults (override via runtime/CRM):
- `assignment_fee` = 15000
- `buyer_cushion` = 0 for “max lock” table; show **safer** line with cushion 10000 optional
- `buy_closing_pct` = 0.02
- `sell_closing_pct` = 0.07
- `hold_reserve` = 8000
- `arv_factor` = 0.70

Default underwriting case for Shane max_price suggestion = **medium** (call out in verdict).

## Formulas (per tier)

```
MAO_flip           = round(ARV * arv_factor - rehab_tier)
you_lock_seller_max = MAO_flip - assignment_fee
flipper_all_in      = MAO_flip
buy_closing         = round(flipper_all_in * buy_closing_pct)
sell_closing        = round(ARV * sell_closing_pct)
total_project_cost  = flipper_all_in + buy_closing + rehab_tier + hold_reserve + sell_closing
flipper_profit      = ARV - total_project_cost
works               = flipper_profit > 0 AND you_lock_seller_max > 0
```

## Markdown footer structure (required order)

1. `## Side-by-side` table (Low | Medium | High)
2. Full `## DEAL RECAP — LOW` block
3. Full `## DEAL RECAP — MEDIUM` block  
4. Full `## DEAL RECAP — HIGH` block

Each tier block:

```markdown
---

## DEAL RECAP — {LOW|MEDIUM|HIGH}

### Roles / stack

| Role | Number |
|------|--------:|
| You lock seller at (max) | ${you_lock_seller_max:,} |
| Your fee | ${assignment_fee:,} |
| Flipper all-in | ${flipper_all_in:,} |
| Flipper rehab | ${rehab:,} |
| Flipper sells (ARV) | ${arv:,} |

**Open range (negotiate under max):** ${open_low:,} – ${open_high:,}  
**Safer lock (extra ${buyer_cushion_safe:,} buyer meat):** ${safer_seller_lock:,}

### Does the flipper still make money?

| | |
|--|--:|
| Purchase | ${flipper_all_in:,} |
| Buy closing ~2% | ${buy_closing:,} |
| Rehab | ${rehab:,} |
| Hold (taxes/ins/util/loan) | ${hold_reserve:,} |
| Sell costs ~7% (commission+closing) | ${sell_closing:,} |
| **Total project cost** | **${total_project_cost:,}** |
| **ARV sale** | **${arv:,}** |
| **Flipper profit** | **${flipper_profit:,}** |

### Verdict

{verdict_paragraph}
```

### Side-by-side table

| | Low | Medium | High |
|--|--:|--:|--:|
| Rehab | | | |
| MAO_flip (flipper all-in) | | | |
| You lock seller (max) | | | |
| Your fee | 15000 | 15000 | 15000 |
| Open range | | | |
| Safer lock (−10k) | | | |
| Flipper profit | | | |
| Works? | YES/NO | YES/NO | YES/NO |

## JSON (required)

- `deal_recap` = **medium** tier object (default case)
- `deal_recap_by_tier` = `{ "low": {...}, "medium": {...}, "high": {...} }`
- Each object includes the fields from `crm/scout_deal_recap.py` (`markdown_footer` optional in by_tier)

Helper: `python3 crm/scout_deal_recap.py <arv> <rehab>`
Build all tiers in report generator by calling `build_deal_recap` three times.
