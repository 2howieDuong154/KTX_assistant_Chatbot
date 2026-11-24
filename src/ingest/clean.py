import re
from collections import Counter

def remove_repeated_lines(pages_text: list[str], ratio=0.5):
    if len(pages_text) <= 2:
        return pages_text
    counter = Counter()
    for t in pages_text:
        counter.update({l.strip() for l in t.splitlines() if l.strip()})
    noisy = {l for l, c in counter.items() if c >= len(pages_text) * ratio}
    return ["\n".join(l for l in t.splitlines() if l.strip() not in noisy) for t in pages_text]

# Real new block: starts with Chapter/Article/clause number or point a)
NEW_BLOCK = re.compile(r"^(Chương\s+[IVXLC\d]+|Điều\s+\d+\.|\d+\.\s|[a-zđ]\)\s)")

def join_lines(text: str) -> str:
    out, after_title = [], False
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        is_title = bool(re.match(r"^Điều\s+\d+\.", line))
        if out and not NEW_BLOCK.match(line) and not after_title:
            out[-1] += " " + line
        else:
            out.append(line)
        after_title = is_title
    return "\n".join(out)