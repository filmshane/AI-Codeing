# Alex — Phone qualify & house intake

## Prompt
- `alex-lead-manager.system.md`

## FAQ DB (seller objections / process Q&A)

**Canonical path:** `/home/shanem/FPI-Corp/Alex/FAQ/`

| Asset | File / dir |
|--------|------------|
| Entries (JSONL) | `FAQ/faq_entries.jsonl` (**242** pairs) |
| Handbook | `FAQ/faq_knowledgebase.md` / `.polished.md` |
| Video index | `FAQ/index.json` |
| Video registry | `FAQ/video_registry.json` |
| Chroma index | `FAQ/chroma/` collection `seller_faq` |
| Chroma meta | `FAQ/chroma_meta.json` |
| Transcripts | `FAQ/transcripts/` |
| Raw research | `FAQ/raw/` |
| Voice snippet | `FAQ/VOICE_AGENT_KB_SNIPPET.md` |

Legacy symlink (skills/old scripts):  
`~/wholesale-voice-agent/kb/realkingkhang-seller-faq` → this FAQ dir

### Query Chroma (example)
```bash
python3 - <<'PY'
import chromadb
from chromadb.config import Settings
client = chromadb.PersistentClient(
    path="/home/shanem/FPI-Corp/Alex/FAQ/chroma",
    settings=Settings(anonymized_telemetry=False),
)
col = client.get_collection("seller_faq")
r = col.query(query_texts=["are you a wholesaler?"], n_results=3)
for doc, meta in zip(r["documents"][0], r["metadatas"][0]):
    print(meta.get("id"), meta.get("category"), doc[:120], "...")
PY
```

Alex should call `retrieve_seller_faq` (or equivalent) against this DB for process/trust objections during qualify.

## Model
- **LLM:** `grok-4.20-reasoning` (Grok 4.2 Reasoning)
- **Auth:** Hermes xAI OAuth via `hermes-proxy-xai` `http://127.0.0.1:8645/v1`
- **Config:** `/home/shanem/FPI-Corp/config/llm.json` + `config/llm.env`
