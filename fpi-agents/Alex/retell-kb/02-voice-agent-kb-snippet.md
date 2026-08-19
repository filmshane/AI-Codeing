# Seller FAQ + Chroma retrieval (wholesale voice agent)

## Paths
- KB root: `/home/shanem/wholesale-voice-agent/kb/realkingkhang-seller-faq`
- Video ID registry: `video_registry.json` (searched / transcribed / faq / chroma flags)
- FAQ JSONL: `faq_entries.jsonl`
- Chroma dir: `chroma/`  collection: **`seller_faq`**
- Meta: `chroma_meta.json`

## Track which YouTube IDs were searched
```bash
PY=/opt/sol-right/.venv/bin/python
SKILL=$HOME/.hermes/skills/research/realkingkhang-seller-faq-kb
OUT=$HOME/wholesale-voice-agent/kb/realkingkhang-seller-faq

$PY $SKILL/scripts/track_and_index_chroma.py --out $OUT --status
# registry fields per video_id: searched, transcribed, faq_extracted, chroma_indexed + timestamps
```

## Rebuild Chroma after FAQ edits
```bash
$PY $SKILL/scripts/track_and_index_chroma.py --out $OUT --build
```

## Fast query (for voice agent tool)
```bash
$PY $SKILL/scripts/query_seller_faq.py --out $OUT \
  --query "seller thinks this is a scam" --top 5
```

Returns: FAQ id, category, full entry, source video_id(s), distance.

## Voice agent rules
1. Retrieve top-k from Chroma for seller utterance.
2. Answer from `voice_agent_answer` + `talking_points`.
3. Never violate `do_not_say`.
4. Deal prices/ARV come from CRM tools — not FAQ.
5. Prefer entries with `extraction=agent_polished`.
