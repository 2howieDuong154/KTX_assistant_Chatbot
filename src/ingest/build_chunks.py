import json, re, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from .chunk import chunk_articles
from .chunk_tables import chunk_penalty_tables
from .chuck_contact import chunk_contact_tables
from .chunk_info import chunk_info_doc

# ---------------- Configuration ----------------
PROCESSED = Path("data/processed")
OUT = PROCESSED / "chunks.jsonl"
DEFAULT_DATE = "2025-09-01"

# Display name used in citations. Files not listed here use their file name.
TITLES = {
    "Noiquy_KTX_trich_092025": "Nội quy KTX Trường ĐH Cần Thơ 2025",
    "ThongTinLienHe": "Hướng dẫn liên hệ công tác",
    "Gioithieu_KTX": "Giới thiệu KTX",
}
EFFECTIVE_DATES = {}          # Example: {"Noiquy_KTX_trich_092025": "2025-09-01"}
PENALTY_TABLE_TITLE = "Phụ lục: Khung xử lý kỷ luật"
# -----------------------------------------------


def slugify(s: str) -> str:
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def read_pages(path: Path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def make_meta(path: Path, doc_type: str):
    stem = path.stem
    pdf_name = pages_source(path)
    return {
        "doc_title": TITLES.get(stem, stem.replace("_", " ")),
        "slug": slugify(stem),
        "doc_type": doc_type,
        "source_file": pdf_name,
        "effective_date": EFFECTIVE_DATES.get(stem, DEFAULT_DATE),
    }


def pages_source(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.loads(f.readline())["source_file"]


def classify(path: Path) -> str:
    name = slugify(path.stem)
    if "noiquy" in name:
        return "rules"
    if "lienhe" in name:
        return "contacts"
    return "info"


def dedupe(chunks):
    """Remove duplicate information chunks. Rule and penalty-table chunks are left unchanged."""
    seen, out, dropped = set(), [], []
    for c in chunks:
        if c["doc_type"] != "thong_tin" or c["chunk_kind"] != "paragraph":
            out.append(c)
            continue
        body = c["text"].split("\n", 1)[-1]
        key = re.sub(r"\W+", "", body.lower())[:200]
        if key in seen:
            dropped.append(c["chunk_id"])
            continue
        seen.add(key)
        out.append(c)
    return out, dropped


def validate(chunks):
    ids = Counter(c["chunk_id"] for c in chunks)
    dup_ids = [i for i, n in ids.items() if n > 1]
    assert not dup_ids, f"chunk_id bị trùng: {dup_ids[:5]}"
    required = ["chunk_id", "text", "doc_type", "doc_title", "section",
                "chunk_kind", "source_file", "effective_date"]
    for c in chunks:
        for k in required:
            assert c.get(k) not in (None, ""), f"{c.get('chunk_id')}: thiếu '{k}'"
        if c["chunk_kind"] != "paragraph" and not c.get("page"):
            print("CẢNH BÁO thiếu page:", c["chunk_id"])


def stats(chunks):
    by = defaultdict(list)
    for c in chunks:
        by[c["chunk_kind"]].append(len(c["text"]))
    print(f"\n{'loại chunk':<20}{'số':>6}{'TB':>8}{'ngắn':>8}{'dài':>8}")
    for k, v in sorted(by.items()):
        print(f"{k:<20}{len(v):>6}{sum(v)//len(v):>8}{min(v):>8}{max(v):>8}")
    print(f"{'TỔNG':<20}{len(chunks):>6}")
    longest = max(chunks, key=lambda c: len(c["text"]))
    shortest = min(chunks, key=lambda c: len(c["text"]))
    print(f"\nDài nhất : {longest['chunk_id']} ({len(longest['text'])} ký tự)")
    print(f"Ngắn nhất: {shortest['chunk_id']} ({len(shortest['text'])} ký tự)")


def main():
    chunks = []
    for path in sorted(PROCESSED.glob("*.jsonl")):
        if path.name == OUT.name:
            continue
        kind = classify(path)
        pages = read_pages(path)
        if kind == "rules":
            meta = make_meta(path, "noi_quy")
            a = chunk_articles(pages, meta)
            t = chunk_penalty_tables(pages, meta, PENALTY_TABLE_TITLE)
            print(f"{path.name:<40} rules    -> {len(a)} điều, {len(t)} dòng phạt")
            chunks += a + t
        elif kind == "contacts":
            meta = make_meta(path, "thong_tin")
            c = chunk_contact_tables(pages, meta)
            print(f"{path.name:<40} contacts -> {len(c)} chunk")
            chunks += c
        else:
            meta = make_meta(path, "thong_tin")
            c = chunk_info_doc(pages, meta)
            print(f"{path.name:<40} info     -> {len(c)} chunk")
            chunks += c

    chunks, dropped = dedupe(chunks)
    if dropped:
        print("\nĐã bỏ chunk trùng:", dropped)

    validate(chunks)

    with open(OUT, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\nĐã ghi {len(chunks)} chunk vào {OUT}")
    stats(chunks)


if __name__ == "__main__":
    main()