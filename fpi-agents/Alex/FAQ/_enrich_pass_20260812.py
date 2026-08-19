#!/usr/bin/env python3
"""Second-pass FAQ enrichment for RealKingKhang seller KB.

Goal resume (2026-08-12):
- Extract polished FAQ for gVVkXCFO8iA + BdL8379aDrA (were faq_extracted=false)
- Double-check all videos; replace thin title_seed stubs with agent_polished
  where transcripts support seller-facing objections
- Regen markdown handbook + rebuild Chroma via skill script
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("/home/shanem/wholesale-voice-agent/kb/realkingkhang-seller-faq")
JSONL = OUT / "faq_entries.jsonl"
MD = OUT / "faq_knowledgebase.md"
MD_POL = OUT / "faq_knowledgebase.polished.md"
REG = OUT / "video_registry.json"
INDEX = OUT / "index.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def src(vid: str, title: str) -> list[dict]:
    return [
        {
            "video_id": vid,
            "title": title,
            "url": f"https://www.youtube.com/watch?v={vid}",
        }
    ]


def e(
    id_: str,
    cat: str,
    q: str,
    a: str,
    tips: list[str],
    dns: list[str],
    vid: str,
    title: str,
) -> dict:
    return {
        "id": id_,
        "category": cat,
        "seller_question_or_complaint": q,
        "voice_agent_answer": a,
        "talking_points": tips,
        "do_not_say": dns
        + [
            "Guaranteed highest price without analysis",
            "Legal advice without a licensed professional",
            "Pressure to sign without written terms",
        ],
        "sources": src(vid, title),
        "extraction": "agent_polished",
    }


# Titles from registry (filled at runtime if missing)
TITLES = {
    "gVVkXCFO8iA": "AI is now replacing human closer",
    "BdL8379aDrA": "My First real estate deal that made me $50,000",
    "4XfLWhv8UpA": "Cold Call New Real Estate Wholesalers",
    "otAcoHlY9h4": "Seller Think it’s a scam but I still Lock it up",
    "LugeMAjzK10": "Watch Me Call Seller Back To Make CASH OFFER",
    "oawOJjUKt_o": "Calling Seller Back To Get A $25,000 Price Reduction",
    "jpyuGLjcLRk": "Helping A subscriber negotiate a deal with Seller LIVE",
    "XPKsa67KqBE": "How To Negotiate Like A Pro As A Real Estate Investor",
    "gyoY7KT6fIc": "AI Help Investor LOCK UP A $25,000 Wholesale Deal",
    "qNg3edteNRk": "AI Lock Up A $35,000 Deal For Investor Less Than 30 Days",
    "K5yank5PwIw": "My AI just help him LOCK up a deal for $15,000 wholesale fee",
    "6HJlJaW0geQ": "He Turn $500 Into $20,000 | Realtor And Wholesaler",
    "o_ZwvGTRVB8": "I Launch My Skool Community To Show You How To Virtually Wholesale real estate for just $57/Month",
    "YAEqfugvdfY": "How to make an extra 5k-10k on your existing wholesale deal without any more work",
    "u5HzJ7e9Zx0": "$6,000 in Fb Ads and generated over $84,000 in wholesale fees",
    "Kzz6LwEKIYo": "Get Insider Tips On Wholesale Real Estate With Our 1on1 Sessions!",
}


def new_entries() -> list[dict]:
    g, gt = "gVVkXCFO8iA", TITLES["gVVkXCFO8iA"]
    b, bt = "BdL8379aDrA", TITLES["BdL8379aDrA"]
    c, ct = "4XfLWhv8UpA", TITLES["4XfLWhv8UpA"]
    dns_ai = ["Joke about being a robot", "Lie about being human if company policy requires disclosure"]

    entries: list[dict] = []

    # --- Priority: gVVkXCFO8iA (live AI closer call) ---
    entries += [
        e(
            "gvv-pace-001",
            "process_confusion",
            "Whoa — can you slow down? You're talking too fast.",
            "Absolutely — thank you for saying that. I'll slow way down. We can take this one question at a time, and if anything is unclear just stop me. Is now still a good time for a short conversation, or would another time work better?",
            [
                "Thank seller for the feedback",
                "Slow pace deliberately",
                "Offer to reschedule if needed",
            ],
            ["Keep rapid-fire pitching"],
            g,
            gt,
        ),
        e(
            "gvv-number-001",
            "process_confusion",
            "Are you someone who can actually give me a number today, or are we just going to talk about the property?",
            "Great question. My job is to go over a few quick details about the property with you, then work toward a real cash offer based on what you share — condition, timeline, and what you need from a sale. I won't invent a number without those basics. Sound fair if we cover a few details first?",
            [
                "Confirm path to a real offer",
                "Need property details first",
                "No invented price",
            ],
            ["Promise a final number with zero property facts"],
            g,
            gt,
        ),
        e(
            "gvv-emotion-001",
            "emotional_attachment",
            "I'm selling after a long divorce / big life change and I just need a fresh start.",
            "I'm sorry you're going through so much — that's a lot of change at once. A lot of owners sell during transitions like divorce or relocation. We can keep this simple: written terms, your timeline, and no pressure to clean or list. What matters most for you on timing — do you need to sell before your next place, or just move on when the numbers work?",
            [
                "Empathy first",
                "Transition / fresh start framing",
                "Ask soft timeline question",
            ],
            ["Minimize the personal situation", "Push a same-day hard close"],
            g,
            gt,
        ),
        e(
            "gvv-mortgage-001",
            "paperwork_title",
            "There's still a mortgage / most of my retirement is in the equity.",
            "Understood — equity is often someone's nest egg, so we treat the numbers carefully. At closing, a licensed title company typically pays off any mortgage and other agreed liens from the proceeds, and you receive the net. I don't need every bank detail on this call, but knowing roughly what's owed helps us talk realistically. About how much is left on the loan, ballpark?",
            [
                "Title pays off mortgage at closing",
                "Seller receives net proceeds",
                "Ask ballpark payoff only",
            ],
            ["Ask for full account numbers on a first call", "Promise a specific net check amount"],
            g,
            gt,
        ),
        e(
            "gvv-repairs-001",
            "repairs_condition",
            "It needs work — maybe $50–75k in materials and labor, or less if I do it myself.",
            "That's helpful context, thank you. We buy as-is, so you don't have to finish renovations for us. We'll factor condition into our offer rather than asking you to spend more money first. Besides the big-ticket items you mentioned, is there anything structural, roof, or foundation we should know about?",
            [
                "As-is purchase",
                "No requirement to renovate first",
                "Invite disclosure of major issues",
            ],
            ["Tell seller to spend money fixing before offer", "Invent repair budgets"],
            g,
            gt,
        ),
        e(
            "gvv-price-001",
            "price_lowball",
            "I've had lowball offers and declined them. I'm pretty firm near my number.",
            "I hear you — and I won't waste your time with a joke offer. Other buyers may have bid low without understanding the property. We'll look at condition, timeline, and what you need to net, then come back with something we can actually close. If we made the process smooth and fast, is there a walk-away number you'd need to see to even consider it — or should we start from your asking and see what's realistic?",
            [
                "Respect prior lowball fatigue",
                "Ask walk-away vs asking",
                "Process + certainty framing",
            ],
            ["Mock prior offers", "Invent Zillow/ARV numbers"],
            g,
            gt,
        ),
        e(
            "gvv-leaseback-001",
            "timeline_urgency",
            "I'd only go lower on an almost overnight deal, and I'd still need a short holdback or leaseback to move.",
            "That makes total sense — speed and a soft landing matter. Many sellers want a quick close plus a few days or weeks after funding to move. If title and numbers work, we can discuss a short post-close occupancy or similar transition in writing. What window would you need after closing to be comfortable?",
            [
                "Acknowledge speed + transition need",
                "Leaseback/occupancy only in writing",
                "Ask required move window",
            ],
            ["Promise free rent indefinitely", "Verbal-only occupancy deals"],
            g,
            gt,
        ),
        e(
            "gvv-ai-001",
            "trust_scam_fear",
            "Just for the record — you're a live person, right? Not AI?",
            "Totally fair question — a lot of people ask that now. I'm here to help you through the sale process and get you a real written offer path with our team. If anything I say is unclear, stop me and I'll explain slower. Want me to text or email a quick summary of who we are and the next step after this call so you have it in writing?",
            [
                "Don't get defensive",
                "Offer written follow-up / identity of company",
                "Focus on process clarity",
            ],
            dns_ai,
            g,
            gt,
        ),
        e(
            "gvv-split-001",
            "paperwork_title",
            "I have to check with my ex — we're splitting equity 50/50.",
            "Understood — when more than one person has a stake, title needs everyone who must sign on the same page. You don't have to resolve every detail tonight. Who would need to be on the agreement, and what's the best email so we can send a clear written outline you can both review?",
            [
                "Multi-party equity / ex-spouse awareness",
                "Title needs proper signers",
                "Collect email for written outline",
            ],
            ["Tell them to ignore the ex's interest", "Legal advice on divorce decrees"],
            g,
            gt,
        ),
        e(
            "gvv-callback-001",
            "followup_ghosting",
            "Is this still the best number to reach me on?",
            "Perfect — I'll stick to this number unless you tell me otherwise. If we get disconnected I'll call right back. Is text okay for a quick written recap after we talk numbers?",
            [
                "Confirm best phone",
                "Permission for text recap",
                "Plan for disconnects",
            ],
            ["Spam multiple numbers without consent"],
            g,
            gt,
        ),
        e(
            "gvv-timeline-001",
            "timeline_urgency",
            "Could you close in about 45–60 days, or faster if things line up?",
            "Yes — many cash closings land in that range depending on title. If you need faster or a little more time, say so and we'll aim the contract dates around your move. What closing window would actually help you most?",
            [
                "Flexible close window",
                "Title-dependent timing",
                "Ask seller preference",
            ],
            ["Guarantee a 3-day close without title check"],
            g,
            gt,
        ),
        e(
            "gvv-open-001",
            "price_lowball",
            "I don't have a hard bottom — I'm open to offers if the deal is smooth.",
            "I appreciate the flexibility. We'll still treat your equity seriously and come back with a written number we can stand behind, not a bait bid. While we run the numbers, what matters more to you if the price is close — speed, as-is condition, or covering closing costs?",
            [
                "Respect openness without lowballing",
                "Clarify non-price priorities",
                "Promise written real offer",
            ],
            ["Exploit openness with insult offer"],
            g,
            gt,
        ),
    ]

    # --- Priority: BdL8379aDrA (origin story + first wholesale) ---
    entries += [
        e(
            "bdl-expired-001",
            "realtor_listing_compare",
            "I listed with an agent, it expired, and it still didn't sell. Now what?",
            "That happens more than people admit — listing is one path, not the only one. A cash as-is buyer can skip showings, repairs for retail buyers, and another round of commissions if the retail path already stalled. I'm happy to look at a simple cash option you can compare next to listing again. What stopped the last listing from closing — price, condition, or timing?",
            [
                "Expired listing empathy",
                "Cash as-is as alternate path",
                "Ask why listing failed",
            ],
            ["Bash the previous agent", "Promise retail price with cash speed"],
            b,
            bt,
        ),
        e(
            "bdl-mail-001",
            "privacy_curiosity",
            "I got a letter saying you'll buy my house for cash with a quick close and no commission — is that legitimate?",
            "Direct mail is a common way cash buyers introduce themselves. A real team will put terms in writing, use a title company, and never ask you to pay upfront fees to 'qualify.' If the letter felt random, I can explain who we are and only continue if you're open to a conversation. Would you rather a quick call now or a written outline by email first?",
            [
                "Normalize direct mail outreach",
                "No upfront fees from seller",
                "Offer written intro",
            ],
            ["Demand secrecy", "Ask seller to wire money to start"],
            b,
            bt,
        ),
        e(
            "bdl-rapport-001",
            "process_confusion",
            "I don't want to sign anything on the first call.",
            "You shouldn't feel rushed. Good deals usually take a few conversations so you understand price, timing, and paperwork. We can talk, I can send a simple written outline, and only if you're comfortable we meet or e-sign later. What would you want clarified before you'd even look at a draft agreement?",
            [
                "No first-call pressure",
                "Multiple touches normal",
                "Written outline before commitment",
            ],
            ["Force same-day signature"],
            b,
            bt,
        ),
        e(
            "bdl-cash-001",
            "process_confusion",
            "What does a cash offer with no realtor commission and quick closing actually mean for me?",
            "In plain terms: we agree on a purchase price and timeline in writing, you generally don't pay a listing commission on this path, and a title company handles the closing so you receive your proceeds when we close. You're not required to fix the home for retail showings. Exact fees and credits should always be spelled out in the contract — I won't invent line items on the phone. Want me to walk the steps from agreement to keys?",
            [
                "Written price + timeline",
                "Title closes; seller gets proceeds at closing",
                "As-is / fewer retail showings",
            ],
            ["Hide that contracts are assignable if company assigns", "Invent fee amounts"],
            b,
            bt,
        ),
        e(
            "bdl-earnest-001",
            "paperwork_title",
            "How do I know you'll actually follow through after we agree?",
            "Serious buyers put the agreement in writing and typically place earnest money with title or as the contract specifies — it's a deposit that shows commitment, not a fee you pay us. Your protections and dates should be in the contract in plain language. I can review those sections with you before you sign. What part worries you most — timeline, price, or what happens if something falls through?",
            [
                "Written contract",
                "Earnest money / commitment via proper channels",
                "Review cancel/protect sections",
            ],
            ["Say contracts are never cancelable", "Ask seller for a deposit to the buyer personally"],
            b,
            bt,
        ),
        e(
            "bdl-asis-001",
            "repairs_condition",
            "I don't want the drama of fixing everything for a picky retail buyer.",
            "That's a big reason owners choose cash as-is. You avoid months of contractor drama, city permit delays, and a retail buyer re-trading repairs. We price the home in its current condition instead of asking you to renovate first. What's the biggest repair headache you'd rather not manage?",
            [
                "As-is avoids retail repair re-trades",
                "No renovate-first requirement",
                "Invite main headache disclosure",
            ],
            ["Promise zero diligence forever"],
            b,
            bt,
        ),
        e(
            "bdl-flex-001",
            "timeline_urgency",
            "What if the buyer needs to change something after we have a deal?",
            "Any change should be discussed openly and put in writing — price, dates, or occupancy. You shouldn't get surprise pressure. If something material changes, we talk and you decide whether the new terms work. Would you want a shorter close, longer close, or a little time after funding to move?",
            [
                "Changes in writing only",
                "Seller decision on material changes",
                "Clarify preferred timeline",
            ],
            ["Verbal side deals that contradict the contract"],
            b,
            bt,
        ),
    ]

    # --- Second pass: cold-call training seller objections (4XfLWhv8UpA) ---
    entries += [
        e(
            "cold-how-number-001",
            "privacy_curiosity",
            "How did you get my number? This call is out of the blue.",
            "Fair question — unexpected calls feel weird. We reach owners who may be open to a cash sale through marketing and public property information our team uses for outreach. If you'd rather not talk, say so and I won't push. If you're even a little curious about a no-obligation cash option, I can explain in two minutes. Which do you prefer?",
            [
                "Validate surprise",
                "High-level marketing/public records framing",
                "Permission to continue",
            ],
            ["Claim random psychic knowledge", "Refuse to explain outreach"],
            c,
            ct,
        ),
        e(
            "cold-scam-001",
            "trust_scam_fear",
            "How do I know you guys aren't some kind of scam?",
            "Completely reasonable. A legitimate buyer will give a clear company name, put terms in writing, and close through a real title company — and won't ask you to pay fees upfront to get an offer. I can send a short email intro and only continue if you're comfortable. Would an email summary help before we go further?",
            [
                "Company identity",
                "Title company close",
                "No upfront seller fees",
                "Offer email intro",
            ],
            ["Just trust me", "Ask for gift cards or wires from seller"],
            c,
            ct,
        ),
        e(
            "cold-notlisted-001",
            "process_confusion",
            "I never listed my house. Why are you calling about buying it?",
            "You don't have to have it listed for a cash buyer to reach out. Some owners never put a sign in the yard but will still listen to a simple as-is option. There's no obligation — if you're not selling, that's fine. Are you open to hearing what a cash offer process looks like, or should I let you go?",
            [
                "Unlisted outreach is normal for cash buyers",
                "No obligation",
                "Binary soft choice",
            ],
            ["Imply they secretly listed"],
            c,
            ct,
        ),
        e(
            "cold-price-right-001",
            "price_lowball",
            "Anything is for sale at the right price — what's your offer?",
            "I love the directness. A responsible offer depends on nearby sales and the home's condition — I won't throw a random number. If you share a quick condition snapshot and what you'd need to net to even consider it, I can work toward a real figure. How would you describe the condition, and is there a number you'd need to see?",
            [
                "No random offer",
                "Condition + seller number",
                "Path to real figure",
            ],
            ["Guess a price with zero facts"],
            c,
            ct,
        ),
        e(
            "cold-fast-offer-001",
            "timeline_urgency",
            "How fast can you actually write a cash offer?",
            "Often we can outline terms within about a day or two once we have basic property details and your goals — sometimes sooner. Closing itself depends on title. If speed matters, tell me your ideal move date and we'll aim the paperwork around that. What's driving the timeline on your side?",
            [
                "Offer outline in 24–48h framing when details known",
                "Close depends on title",
                "Ask seller driver",
            ],
            ["Guarantee same-hour close"],
            c,
            ct,
        ),
    ]

    # --- Second pass: process clarity from education-heavy videos ---
    entries += [
        e(
            "proc-wholesale-001",
            "process_confusion",
            "Are you the actual buyer or a middleman wholesaling my contract?",
            "Transparency matters. Our team works cash purchase agreements and may partner with end buyers depending on the file — either way you should see clear written terms, who is on the contract, and a title company closing. I'll explain our exact structure for your deal in plain English before you sign. What matters more to you: knowing who funds the purchase, or simply a clean close on the date and price we agree?",
            [
                "Honest structure disclosure",
                "Written terms + title",
                "Ask seller priority",
            ],
            ["Hide assignment if used", "Pretend every file is owner-occupant retail"],
            "BdL8379aDrA",
            bt,
        ),
        e(
            "proc-virtual-001",
            "process_confusion",
            "Can this whole cash sale happen without me doing a big retail listing process?",
            "Yes — that's the point of a direct cash path for many owners. You can often skip open houses, endless showings, and listing prep. We still need honest property info and a proper closing. If you want, we start with a short call, then written terms. Would you rather start with condition and timeline, or with what you need to net?",
            [
                "Direct sale vs retail listing labor",
                "Still need honesty + title close",
                "Offer two starting points",
            ],
            ["Promise zero questions ever"],
            "o_ZwvGTRVB8",
            TITLES["o_ZwvGTRVB8"],
        ),
        e(
            "agent-wholesale-001",
            "realtor_listing_compare",
            "I'm a realtor / I know agents — why would I sell to a cash buyer?",
            "Agents are great for many retail sales. Cash as-is is a different tool: fewer showings, less repair theater, and a timeline built around certainty. Some agents even use both paths depending on the seller's goals. If retail still fits, no hard feelings. If you want a clean exit on this property, we can price a cash option you can compare. What outcome matters most — max retail upside or speed and certainty?",
            [
                "Respect agent channel",
                "Position cash as alternate tool",
                "Compare goals not egos",
            ],
            ["Insult realtors", "Claim agents never help sellers"],
            "6HJlJaW0geQ",
            TITLES["6HJlJaW0geQ"],
        ),
    ]

    return entries


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def save_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def rebuild_markdown(rows: list[dict]) -> str:
    # Prefer polished non-title_seed
    use = [r for r in rows if r.get("extraction") != "title_seed"]
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for r in use:
        by_cat[str(r.get("category") or "uncategorized")].append(r)

    ts = now()
    lines = [
        "# Wholesale Seller FAQ Knowledge Base (Voice Agent)",
        "",
        f"_Updated {ts} — agent second-pass enrichment (gVVkXCFO8iA, BdL8379aDrA + cold-call/process pass)._",
        "",
        f"**Entries:** {len(use)} production Q&As in markdown/jsonl (title_seed stubs excluded from handbook).",
        "",
        "**Rules:** Acknowledge → clarify → proof/next step → one question. No invented prices. Title/attorney for legal.",
        "",
    ]
    for cat in sorted(by_cat.keys()):
        lines.append(f"## {cat}")
        lines.append("")
        for r in sorted(by_cat[cat], key=lambda x: str(x.get("id") or "")):
            rid = r.get("id") or "unknown"
            q = r.get("seller_question_or_complaint") or ""
            a = r.get("voice_agent_answer") or ""
            tips = r.get("talking_points") or []
            lines.append(f"### {rid}")
            lines.append("")
            lines.append(f"**Seller:** {q}")
            lines.append("")
            lines.append(f"**Agent:** {a}")
            lines.append("")
            if tips:
                lines.append("**Talking points:**")
                for t in tips:
                    lines.append(f"- {t}")
                lines.append("")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def update_registry(rows: list[dict]) -> dict:
    reg = json.loads(REG.read_text()) if REG.exists() else {"videos": {}, "channel": ""}
    videos = reg.setdefault("videos", {})
    # map video -> entry ids
    by_vid: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        if r.get("extraction") == "title_seed":
            continue
        eid = r.get("id")
        for s in r.get("sources") or []:
            vid = s.get("video_id")
            if vid and eid:
                by_vid[vid].append(eid)

    ts = now()
    # ensure all transcript files represented
    for p in sorted((OUT / "transcripts").glob("*.txt")):
        vid = p.stem
        rec = videos.setdefault(
            vid,
            {
                "video_id": vid,
                "title": TITLES.get(vid, vid),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "discovered_at": ts,
            },
        )
        rec["searched"] = True
        rec["transcribed"] = True
        rec["transcript_path"] = str(p)
        rec["transcript_chars"] = p.stat().st_size
        rec.setdefault("title", TITLES.get(vid, rec.get("title") or vid))
        rec.setdefault("url", f"https://www.youtube.com/watch?v={vid}")
        if by_vid.get(vid):
            rec["faq_extracted"] = True
            rec["faq_extracted_at"] = ts
            # merge ids unique
            existing = list(rec.get("faq_entry_ids") or [])
            for eid in by_vid[vid]:
                if eid not in existing:
                    existing.append(eid)
            rec["faq_entry_ids"] = existing
        rec["last_seen_at"] = ts

    reg["updated_at"] = ts
    reg["counts"] = {
        "videos_tracked": len(videos),
        "searched": sum(1 for v in videos.values() if v.get("searched")),
        "transcribed": sum(1 for v in videos.values() if v.get("transcribed")),
        "faq_extracted": sum(1 for v in videos.values() if v.get("faq_extracted")),
        "chroma_indexed": sum(1 for v in videos.values() if v.get("chroma_indexed")),
    }
    REG.write_text(json.dumps(reg, indent=2) + "\n")
    return reg


def main() -> None:
    # Load titles from registry if present
    if REG.exists():
        reg = json.loads(REG.read_text())
        for vid, v in (reg.get("videos") or {}).items():
            if v.get("title"):
                TITLES[vid] = v["title"]

    old = load_jsonl(JSONL)
    new = new_entries()
    new_ids = {r["id"] for r in new}
    new_vids = set()
    for r in new:
        for s in r.get("sources") or []:
            if s.get("video_id"):
                new_vids.add(s["video_id"])

    # Drop title_seed stubs for videos we enriched; drop any prior ids we replace
    kept = []
    dropped = 0
    for r in old:
        rid = r.get("id")
        if rid in new_ids:
            dropped += 1
            continue
        if r.get("extraction") == "title_seed":
            srcs = r.get("sources") or []
            vids = {s.get("video_id") for s in srcs}
            # drop title seeds for videos that now have polished adds, or any title seed
            # for priority vids / cold call / process upgrades
            if vids & new_vids or rid.startswith("src-"):
                # Keep title seeds only for videos with no new polished coverage at all
                if vids & new_vids:
                    dropped += 1
                    continue
                # For src-* where we didn't add coverage, keep for now unless empty value
        kept.append(r)

    # Specifically remove title seeds for videos that received real entries
    kept2 = []
    for r in kept:
        if r.get("extraction") == "title_seed":
            vids = {s.get("video_id") for s in (r.get("sources") or [])}
            if vids & new_vids:
                dropped += 1
                continue
        kept2.append(r)

    merged = kept2 + new
    # de-dupe by id last wins
    by_id = {}
    for r in merged:
        if r.get("id"):
            by_id[r["id"]] = r
    final = list(by_id.values())
    final.sort(key=lambda r: (str(r.get("category") or ""), str(r.get("id") or "")))

    save_jsonl(JSONL, final)
    md = rebuild_markdown(final)
    MD.write_text(md)
    MD_POL.write_text(md)
    reg = update_registry(final)

    # stats
    from collections import Counter

    ext = Counter(r.get("extraction") for r in final)
    cats = Counter(r.get("category") for r in final)
    print("merged_entries", len(final))
    print("added", len(new), "dropped", dropped)
    print("extraction", dict(ext))
    print("categories", dict(cats))
    print("registry_counts", reg.get("counts"))
    # verify priority vids
    for vid in ("gVVkXCFO8iA", "BdL8379aDrA"):
        v = reg["videos"].get(vid, {})
        print(
            vid,
            "faq_extracted",
            v.get("faq_extracted"),
            "faq_ids",
            len(v.get("faq_entry_ids") or []),
        )


if __name__ == "__main__":
    main()
