import json, re
from pathlib import Path
import pdfplumber

def clean_cell(c):
    return re.sub(r"\s+", " ", c).strip() if c else ""

def fill_down(rows):
    """Fill merged or empty cells by repeating the value from the previous row in the first column."""
    prev = []
    out = []
    for row in rows:
        row = [clean_cell(c) for c in row]
        for j, c in enumerate(row):
            if not c and j < len(prev) and j == 0:   # fill only the group/number column
                row[j] = prev[j]
        out.append(row)
        prev = row
    return out

def parse_pdf(path: Path):
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            found = page.find_tables()
            boxes = [t.bbox for t in found]

            def outside_tables(obj):
                return not any(
                    obj["x0"] >= x0 - 1 and obj["x1"] <= x1 + 1
                    and obj["top"] >= t - 1 and obj["bottom"] <= b + 1
                    for x0, t, x1, b in boxes
                )

            text = page.filter(outside_tables).extract_text() or ""
            tables = [[[clean_cell(c) for c in row] for row in t.extract()] for t in found]
            pages.append({"page": i, "text": text, "tables": tables})
    return pages

if __name__ == "__main__":
    out_dir = Path("data/processed"); out_dir.mkdir(parents=True, exist_ok=True)
    for pdf_path in Path("data/raw").rglob("*.pdf"):
        pages = parse_pdf(pdf_path)
        with open(out_dir / f"{pdf_path.stem}.jsonl", "w", encoding="utf-8") as f:
            for p in pages:
                f.write(json.dumps({"source_file": pdf_path.name, **p}, ensure_ascii=False) + "\n")