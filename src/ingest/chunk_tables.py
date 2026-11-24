import re


# ---------- Utilities ----------
def _split_behaviors(content: str):
    """Split the content cell into behaviors using the '- ' bullet marker."""
    items = re.split(r"(?:^|\s)-\s+", content.strip())
    return [i.strip().rstrip(".") for i in items if i.strip()]


def _is_header_row(row):
    """Header row: No. / Violation / Occurrence 1... (including repeated headers on each page)."""
    cells = [c.strip() for c in row]
    if not any(cells):
        return False
    return (
        cells[0].lower() == "stt"
        or (len(cells) > 1 and cells[1].lower() == "nội dung vi phạm")
        or any(c.startswith("Lần 1") for c in cells)
    )


def _is_new_subrow(r):
    """Create a subrow when the number is blank but the violation and handling differ.
    For example, item 12 may have two rows under the same vertically merged number."""
    return (not r[0]) and bool(r[1]) and any(r[2:5])


def _format_handling(l1, l2, l3, note):
    only_first = bool(l1) and not l2 and not l3
    if only_first and len(l1) > 60:
        # Shared handling for all occurrences (items 1, 4, 5): a long description not split by occurrence.
        text = f"Áp dụng chung (không chia theo số lần): {l1}"
        kind = "chung"
    else:
        parts = []
        for label, v in (("Vi phạm lần 1", l1), ("Vi phạm lần 2", l2), ("Vi phạm lần 3", l3)):
            if v:
                parts.append(f"{label}: {v}.")
        text = " ".join(parts)
        kind = "theo_lan"
    if note:
        text += f" Ghi chú: {note}."
    return text, kind


# ---------- Main function ----------
def chunk_penalty_tables(pages, doc_meta, table_title):
    """pages: list of dictionaries read from JSONL (each contains 'page' and 'tables')."""

    # 1. Merge data rows from all pages and remove header rows.
    rows_all = []
    for p in pages:
        for tbl in p["tables"]:
            for r in tbl:
                if _is_header_row(r):
                    continue
                r = [(c or "").strip() for c in r] + [""] * 6
                r = r[:6]
                if any(r):
                    rows_all.append((p["page"], r))

    # 2. Handle blank numbers: create subrows or merge overflow text from the previous page.
    merged = []
    for page, r in rows_all:
        if not r[0] and merged:
            if _is_new_subrow(r):
                r[0] = merged[-1][1][0]          # subrow: reuse the number from the preceding item
                merged.append((page, r))
            else:                                # overflow text: append it to the previous row
                for j in range(6):
                    if r[j]:
                        merged[-1][1][j] = (merged[-1][1][j] + " " + r[j]).strip()
        else:
            merged.append((page, r))

    # 3. Create chunks and ensure that chunk_id remains unique.
    chunks, used, seq = [], set(), {}
    for page, (stt, content, l1, l2, l3, note) in merged:
        if not stt or not content:
            continue
        seq[stt] = seq.get(stt, 0) + 1
        sub = seq[stt]                           # subrow index for this item
        handling, kind = _format_handling(l1, l2, l3, note)

        for i, behavior in enumerate(_split_behaviors(content), start=1):
            cid = f"{doc_meta['slug']}_penalty_{stt}_{sub}_{i}"
            if cid in used:
                n = 2
                while f"{cid}_dup{n}" in used:
                    n += 1
                print(f"WARNING: duplicate {cid} on page {page}; renamed to _dup{n}")
                cid = f"{cid}_dup{n}"
            used.add(cid)

            chunks.append({
                "chunk_id": cid,
                "text": (
                    f"[{doc_meta['doc_title']} > {table_title} > Mục {stt}]\n"
                    f"Hành vi vi phạm: {behavior}.\n"
                    f"Hình thức xử lý: {handling}"
                ),
                "section": f"{table_title} - Mục {stt}",
                "chunk_kind": "penalty_row",
                "handling_type": kind,
                "page": page,
                **doc_meta,
            })
    return chunks