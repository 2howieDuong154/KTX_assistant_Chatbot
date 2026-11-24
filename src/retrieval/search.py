from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient

embedder = SentenceTransformer("BAAI/bge-m3")
reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", max_length=512)
client = QdrantClient(url="http://localhost:6333")

RERANK_THRESHOLD = 0.3      # tune with the evaluation data below

def qdrant_search(query, limit=20):
    qv = embedder.encode(query, normalize_embeddings=True).tolist()
    return client.query_points("dorm_docs", query=qv, limit=limit, with_payload=True).points

def relevance_filter(query, hits, top_k=5, threshold=RERANK_THRESHOLD):
    if not hits:
        return []
    scores = reranker.predict([(query, h.payload["text"]) for h in hits],
                              activation_fn=__import__("torch").nn.Sigmoid())
    ranked = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)
    return [{"rerank_score": float(s), **h.payload}
            for h, s in ranked[:top_k] if s >= threshold]

def retrieve(query):
    hits = qdrant_search(query, limit=20)       # retrieve broadly, then let the reranker filter
    return relevance_filter(query, hits)