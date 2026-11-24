import json, sys
from pathlib import Path

for f in sorted(Path("data/processed").glob("*.jsonl")):
    pages = [json.loads(l) for l in open(f, encoding="utf-8")]
    n_tables = sum(len(p["tables"]) for p in pages)
    print(f"\n=== {f.name}: {len(pages)} trang, {n_tables} bảng ===")
    print(pages[0]["text"][:800])            # beginning of page 1
    for p in pages:
        for t in p["tables"][:1]:
            print(f"-- bảng ở trang {p['page']}, {len(t)} dòng:")
            for row in t[:4]:
                print(row)
            break