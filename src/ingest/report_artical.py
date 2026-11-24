import json
from .chunk import chunk_articles

pages = [json.loads(l) for l in open("data/processed/Noiquy_KTX_trich_092025.jsonl", encoding="utf-8")]
meta = {"doc_title": "Nội quy KTX", "slug": "noiquy", "doc_type": "noi_quy",
        "source_file": "Noiquy_KTX_trich_092025.pdf", "effective_date": "2025-09-01"}
ch = chunk_articles(pages, meta)
print("Tổng chunk:", len(ch), "| dài nhất:", max(len(c["text"]) for c in ch))
for c in ch:
    print(f'{c["chunk_id"]:<22} trang {c["page"]}  {len(c["text"]):>5} ký tự  {c["section"][:500]} :: {c["text"][:500]}')