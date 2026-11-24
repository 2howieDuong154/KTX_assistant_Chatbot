import re
from .clean import join_lines, remove_repeated_lines

DIEU = re.compile(r"(?=^Điều\s+\d+\.)", re.MULTILINE)
DIEU_NUM = re.compile(r"^Điều\s+(\d+)\.", re.MULTILINE)
KHOAN = re.compile(r"(?=^\d+\.\s)", re.MULTILINE)

def chunk_articles(pages, doc_meta, max_chars=1200):
    """pages: list of dictionaries read from JSONL (contains 'page' and 'text')."""
    texts = remove_repeated_lines([p["text"] for p in pages])

    # First page of each article (used for citations)
    page_of = {}
    for p, t in zip(pages, texts):
        for m in DIEU_NUM.finditer(t):
            page_of.setdefault(int(m.group(1)), p["page"])

    full = "\n".join(texts)
    full = re.split(r"^PHỤ LỤC", full, flags=re.MULTILINE)[0]   # remove the appendix
    text = join_lines(full)

    chunks = []
    for art in DIEU.split(text):
        art = art.strip()
        m = DIEU_NUM.match(art)
        if not m:                       # content before Article 1
            continue
        num = int(m.group(1))
        title, _, body = art.partition("\n")

        if len(art) <= max_chars:
            parts = [body.strip()]
        else:                           # for long articles, group clauses up to max_chars
            parts, buf = [], ""
            for k in filter(None, KHOAN.split(body)):
                if buf and len(buf) + len(k) > max_chars:
                    parts.append(buf.strip())
                    buf = ""
                buf += k.strip() + "\n"
            if buf.strip():
                parts.append(buf.strip())

        for i, part in enumerate(parts, start=1):
            suffix = f" (phần {i}/{len(parts)})" if len(parts) > 1 else ""
            chunks.append({
                "chunk_id": f"{doc_meta['slug']}_dieu{num}_p{i}",
                "text": f"[{doc_meta['doc_title']} > {title}{suffix}]\n{part}",
                "section": title,
                "article_no": num,
                "chunk_kind": "article",
                "page": page_of.get(num),
                **doc_meta,
            })
    return chunks