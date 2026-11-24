import re

EMAIL = re.compile(r"[\w.\-]+@[\w.\-]+\.\w+")
UPPER = re.compile(r"^[A-ZÀ-ỴĐ\s]+$")
TOP_ITEM = re.compile(r"(?:^|\s)-\s+(?=\S)")      # "- " marks a main item
# Note: "+ " is preserved within the parent item.

def _norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("\n", " ")).strip()

def _items(cell):
    cell = _norm(cell)
    parts = TOP_ITEM.split(" " + cell)
    return [p.strip().rstrip(";.") for p in parts if p.strip()]

def _is_unit_row(left):
    return bool(UPPER.match(left)) and "Email" not in left

def _parse_person(left):
    left = _norm(left)
    email = (EMAIL.search(left) or [None])[0]
    rest = re.sub(r"Email\s*:?\s*\S+", "", left).strip(" -:")
    name, _, title = rest.partition(" - ")
    # If name and title run together without " - ", preserve the uppercase name portion.
    if not title:
        m = re.match(r"^([A-ZÀ-ỴĐ\s]+?)\s+(?=[A-ZÀ-ỴĐ][a-zà-ỹ])", rest)
        if m and len(m.group(1).split()) >= 2:
            name, title = m.group(1).strip(), rest[m.end():].strip()
    return name.strip(), title.strip(), email

def chunk_contact_tables(pages, doc_meta):
    chunks, unit, unit_info, n = [], "", [], 0
    for p in pages:
        for tbl in p["tables"]:
            for row in tbl:
                row = [_norm(c) for c in row] + ["", ""]
                left, right = row[0], row[1]
                if not left:
                    continue
                if _is_unit_row(left):
                    unit, unit_info = left, _items(right)
                    n += 1
                    body = "\n".join([f"Đơn vị: {unit}"] + [f"- {i}" for i in unit_info])
                    chunks.append(_mk(doc_meta, p["page"], n, "unit", unit, body))
                    continue
                name, title, email = _parse_person(left)
                lines = [f"Người liên hệ: {name}"]
                if title: lines.append(f"Chức vụ: {title}")
                if email: lines.append(f"Email: {email}")
                if unit and right:           # unit leader: the right cell is blank and is outside the group
                    lines.append(f"Đơn vị: {unit}")
                    lines += [f"Thông tin đơn vị: {i}" for i in unit_info]
                if right:
                    lines.append("Nhiệm vụ phụ trách:")
                    lines += [f"- {i}" for i in _items(right)]
                n += 1
                chunks.append(_mk(doc_meta, p["page"], n, "person", name, "\n".join(lines)))
    return chunks

def _mk(meta, page, n, kind, section, body):
    return {"chunk_id": f"{meta['slug']}_contact_{n}",
            "text": f"[{meta['doc_title']} > {section}]\n{body}",
            "section": section, "chunk_kind": f"contact_{kind}",
            "page": page, **meta}