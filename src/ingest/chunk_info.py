import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]")
BULLET = re.compile(r"^\s*[-+•]\s+")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=900, chunk_overlap=0,
    separators=["\n\n", "\n", ". ", "; ", " "],
)

def clean_info_text(pages_text, title):
    text = "\n".join(pages_text)
    text = EMOJI.sub("", text)
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s == title:                                   # repeated title
            continue
        if re.fullmatch(re.escape(title) + r"\s*\d*", s):  # footer "Title 1"
            continue
        out.append(s)
    return out

def to_blocks(lines):
    """Group text into blocks: join wrapped paragraphs and keep lead-ins with their lists."""
    blocks, cur = [], []
    for ln in lines:
        if BULLET.match(ln):
            cur.append(ln)                       # list item
        elif cur and not BULLET.match(cur[-1]) and not cur[-1].endswith((".", ":", ";")):
            cur[-1] += " " + ln                  # join a line wrapped in the middle of a sentence
        elif cur and BULLET.match(cur[-1]):
            # Continue a list item if it has not ended with punctuation.
            if not cur[-1].endswith((".", ";", ":", "…")):
                cur[-1] += " " + ln
            else:
                blocks.append("\n".join(cur)); cur = [ln]
        else:
            if cur and cur[-1].endswith(":"):
                cur.append(ln)
            else:
                if cur: blocks.append("\n".join(cur))
                cur = [ln]
    if cur:
        blocks.append("\n".join(cur))
    return blocks

def chunk_info_doc(pages, doc_meta, max_chars=900):
    title = doc_meta["doc_title"]
    lines = clean_info_text([p["text"] for p in pages], title)
    blocks = to_blocks(lines)

    # Merge adjacent short blocks up to max_chars.
    merged, buf = [], ""
    for b in blocks:
        if buf and len(buf) + len(b) > max_chars:
            merged.append(buf); buf = ""
        buf += ("\n" if buf else "") + b
    if buf: merged.append(buf)

    chunks = []
    for i, m in enumerate(merged, 1):
        for j, piece in enumerate(splitter.split_text(m) if len(m) > max_chars else [m], 1):
            chunks.append({
                "chunk_id": f"{doc_meta['slug']}_{i}_{j}",
                "text": f"[{title}]\n{piece}",
                "section": title, "chunk_kind": "paragraph",
                "page": pages[0]["page"], **doc_meta,
            })
    return chunks


