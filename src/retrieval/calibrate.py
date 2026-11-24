from .search import qdrant_search, reranker
import torch

CAN_ANSWER = ["Tiếp người khác giới trong phòng bị xử lý thế nào?",
              "Ai phụ trách tiếp nhận thông tin sửa chữa KTX A?",
              "KTX có những tiện ích gì?"]
CANNOT = ["Học phí ngành Y bao nhiêu?", "Trường có bao nhiêu khoa?", "Thời tiết Cần Thơ hôm nay?"]

# def top_score(q):
#     hits = qdrant_search(q, 20)
#     s = reranker.predict([(q, h.payload["text"]) for h in hits], activation_fn=torch.nn.Sigmoid())
#     return float(max(s))
#
# for name, qs in (("HAS ANSWER", CAN_ANSWER), ("NO ANSWER", CANNOT)):
#     print("==", name)
#     for q in qs:
#         print(f"{top_score(q):.3f}  {q}")


import json
for l in open("data/processed/chunks.jsonl", encoding="utf-8"):
    c = json.loads(l)
    if c["chunk_id"] in ("thongtinlienhe_contact_3", "thongtinlienhe_contact_4"):
        print(c["text"]); print("-----")