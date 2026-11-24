import json, uuid
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, PayloadSchemaType

CHUNKS = Path("data/processed/chunks.jsonl")
COLLECTION = "dorm_docs"
MODEL = "BAAI/bge-m3"

def main():
  chunks = [json.loads(l) for l in open(CHUNKS, encoding="utf-8") if l.strip()]
  print("Chunk count:", len(chunks))

  model = SentenceTransformer(MODEL)
  client = QdrantClient(url="http://localhost:6333")

  # Recreate the collection so repeated indexing does not leave duplicate records.
  if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)
  client.create_collection(
    COLLECTION,
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
  )
  for field in ("doc_type", "chunk_kind"):
    client.create_payload_index(COLLECTION, field, PayloadSchemaType.KEYWORD)

  vectors = model.encode([c["text"] for c in chunks], normalize_embeddings=True,
                         batch_size=16, show_progress_bar=True)

  points = [
    PointStruct(
      id=str(uuid.uuid5(uuid.NAMESPACE_URL, c["chunk_id"])),  # stable ID derived from chunk_id
      vector=v.tolist(),
      payload=c,
    )
    for c, v in zip(chunks, vectors)
  ]
  client.upsert(COLLECTION, points, wait=True)
  print("Indexed:", client.count(COLLECTION).count, "points")

if __name__ == "__main__":
  main()