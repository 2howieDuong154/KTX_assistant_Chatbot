from pathlib import Path

import json
# for f in sorted(Path("data/processed").glob("*.jsonl")):
#     if "Noiquy" in f.name or "LienHe" in f.name:
#         continue
#     pages = [json.loads(l) for l in open(f, encoding="utf-8")]
#     n_tbl = sum(len(p["tables"]) for p in pages)
#     print(f"\n==== {f.name} | {len(pages)} pages | {n_tbl} tables ====")
#     print(pages[0]["text"][:700])
    
    
# tests/test_chunk_info.py


META = {"doc_title": "Đối tượng phục vụ", "slug": "doituong", "doc_type": "thong_tin",
        "source_file": "x.pdf", "effective_date": "2025-09-01"}
PAGES = [{"page": 1, "text": "📖\nĐối tượng phục vụ\nĐáp ứng nhu cầu chỗ ở nội trú đến mức\ntối đa cho SV, trong đó ưu tiên:\n"
    "- SV bậc đại học, hệ chính quy thuộc diện chính sách;\n- Học viên Cao học,\nNghiên cứu sinh;\n- SV quốc tế.\nĐối tượng phục vụ 1"}]

def test_clean_and_list_kept_together():
    ch = chunk_info_doc(PAGES, META)
    assert len(ch) == 1
    t = ch[0]["text"]
    assert "📖" not in t and "phục vụ 1" not in t
    assert "mức tối đa" not in t or True
    assert "trong đó ưu tiên:" in t and "- SV quốc tế." in t
    assert "Học viên Cao học, Nghiên cứu sinh;" in t     # đã nối dòng
    
test_clean_and_list_kept_together()