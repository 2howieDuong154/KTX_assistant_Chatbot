from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

model = SentenceTransformer("BAAI/bge-m3")
client = QdrantClient(url="http://localhost:6333")

for q in ["Tiếp người khác giới trong phòng bị xử lý thế nào?",
          "Ai phụ trách tiếp nhận thông tin sửa chữa KTX A?",
          "KTX có những tiện ích gì?",
          "Học phí ngành Y bao nhiêu?"]:          # question without an answer
    hits = client.query_points("dorm_docs", query=model.encode(q, normalize_embeddings=True).tolist(),
                               limit=5, with_payload=True).points
    print("\n###", q)
    for h in hits:
        print(f"{h.score:.3f}  {h.payload['chunk_id']}")