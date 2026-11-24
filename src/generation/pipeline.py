from src.retrieval.search import retrieve
from src.generation.answer import generate_answer

NO_INFO = ("Tài liệu hiện có không chứa thông tin để trả lời. "
           "Bạn vui lòng liên hệ Ban quản lý KTX của Trường nhé.")

def ask(query: str) -> dict:
    chunks = retrieve(query)          # filtered by reranker and threshold
    if not chunks:
        return {"answer": NO_INFO, "sources": []}
    return generate_answer(query, chunks)