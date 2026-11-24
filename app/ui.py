import sys
from pathlib import Path

# Add the project root to import `src` regardless of Chainlit's working directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import chainlit as cl
from src.generation.pipeline import ask

DISCLAIMER = "_Thông tin có thể tổng hợp chưa đầy đủ, vui lòng vào trang web chính thức của KTX Trường ĐH Cần Thơ để xem chi tiết._"

STARTERS = [
    ("Ai được ưu tiên vào ở KTX?", "Ai được ưu tiên vào ở KTX?"),
    ("Tiếp người khác giới bị xử lý thế nào?", "Tiếp người khác giới trong phòng bị xử lý thế nào?"),
    ("Tiện ích của KTX", "KTX có những tiện ích gì?"),
    ("Liên hệ sửa chữa KTX A", "Ai phụ trách tiếp nhận thông tin sửa chữa KTX A?"),
]


@cl.set_starters
async def set_starters():
    return [cl.Starter(label=l, message=m) for l, m in STARTERS]


@cl.on_chat_start
async def start():
    await cl.Message(
        content="Xin chào! Mình trả lời câu hỏi về **nội quy, thông tin và liên hệ KTX Trường ĐH Cần Thơ** "
                "dựa trên tài liệu chính thức.\n\n" + DISCLAIMER
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    query = message.content.strip()
    if not query:
        return

    try:
        # ask() is synchronous and potentially expensive, so run it in a separate thread to keep the UI responsive.
        result = await cl.make_async(ask)(query)
    except Exception as e:
        await cl.Message(content=f"Có lỗi khi xử lý câu hỏi: `{type(e).__name__}`. "
                                 "Bạn thử lại sau ít phút.").send()
        print("LỖI:", repr(e))
        return

    answer = result["answer"]
    sources = result.get("sources", [])

    if sources:
        lines = []
        for s in sources:
            page = f", trang {s['page']}" if s.get("page") else ""
            lines.append(f"- **[{s['id']}]** {s['title']} – {s['section']}{page}")
        answer += "\n\n---\n**Nguồn tham khảo**\n" + "\n".join(lines)

    await cl.Message(content=answer).send()