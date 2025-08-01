# app/routes/chatbot.py

import asyncio
import logging
from typing import List
import anyio
from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.auth.dependencies import get_current_user
from app.models.documents import Document
from app.models.chat import ChatHistory
from app.auth.models import User
from app.services.rag import (
    get_rag_chain,
    get_rag_streaming_chain,
    FastAPIStreamingCallbackHandler,
    get_llm_by_domain,
)
from app.services.firewall import get_client_ip, add_firewall_rule
from app.schemas import ChatResponse
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)
router = APIRouter()

# 🧠 DuckDuckGo web fallback
def duckduckgo_search(query: str, max_results=3) -> str:
    with DDGS() as ddgs:
        results = ddgs.text(query)
        output = ""
        for i, r in enumerate(results, 1):
            if i > max_results:
                break
            output += f"{i}. {r['title']}\n{r['body']}\n{r['href']}\n\n"
        return output or "No relevant search result found."

# 🚀 Non-Streaming Chat
@router.post("/chat", response_model=ChatResponse)
def chat_with_existing_documents(
    request: Request,
    question: str = Form(...),
    doc_names: List[str] = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip = get_client_ip(request)
    if not add_firewall_rule(ip):
        raise HTTPException(status_code=500, detail="⚠️ Could not whitelist your IP to access SQL server")

    if not doc_names:
        raise HTTPException(status_code=400, detail="Select at least one document.")

    doc = db.query(Document).filter_by(user_id=current_user.id, name=doc_names[0]).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    try:
        chain = get_rag_chain(
            user_id=str(current_user.id),
            file_path=doc.blob_url,
            domain=doc.domain
        )
        prompt = f"""You are a helpful assistant. Answer the following question clearly:

Question: {question}
Answer:"""

        output = chain.invoke(prompt)
        answer = output["answer"]

        chat = ChatHistory(
            user_id=current_user.id,
            doc_id=doc.id,
            question=question,
            answer=answer,
            domain=doc.domain
        )
        db.add(chat)
        db.commit()

    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(reply=answer)


# 🔁 Streaming Chat with Markdown & DuckDuckGo fallback
@router.post("/chat/stream", response_class=StreamingResponse)
async def stream_chat_with_existing_documents(
    question: str = Form(...),
    doc_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("🟢 /chat/stream HIT")
    print(f"👤 User ID: {current_user.id}")
    print(f"📄 Doc Name: {doc_name}")
    print(f"❓ Question: {question}")

    doc = db.query(Document).filter_by(user_id=current_user.id, name=doc_name).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    handler = FastAPIStreamingCallbackHandler()

    try:
        # ✅ Unpack all 3 values returned
        rag_chain, search_tool, llm = get_rag_streaming_chain(
            str(current_user.id),
            doc.blob_url,
            doc.domain,
            handler
        )
    except Exception as e:
        logger.exception("❌ Failed to build RAG streaming chain")
        raise HTTPException(status_code=500, detail="RAG chain init failed.")

    async def event_generator():
        buffer = ""

        async with anyio.create_task_group() as tg:
            async def run_chain():
                try:
                    result = await rag_chain.acall({"question": question})
                    answer = result.get("answer", "").strip()

                    fallback_phrases = [
                        "i don't know", "not sure", "not provided",
                        "sorry", "unavailable", "couldn’t", "not found", ""
                    ]

                    if any(k in answer.lower() for k in fallback_phrases) or len(answer) < 5:
                        print("⚠️ Weak RAG answer detected — using DuckDuckGo fallback...")
                        web_data = duckduckgo_search(question)

                        prompt = f"""
You are an intelligent assistant. The document failed to answer the user's question.

Here is a web result that might help:

--- Web Result ---
{web_data}
------------------

Q: {question}
A:"""

                        async for chunk in llm.astream(prompt.strip()):
                            await handler.queue.put(chunk)
                    else:
                        await handler.queue.put(answer)

                except Exception:
                    logger.exception("❌ Fallback also failed")
                    await handler.queue.put("Sorry, I couldn’t retrieve any information.")
                await handler.queue.put(None)

            tg.start_soon(run_chain)

            while True:
                token = await handler.queue.get()
                if token is None:
                    break

                buffer += token
                if any(p in token for p in [".", ",", "!", "?", " "]) or len(buffer) > 10:
                    cleaned = (
                        buffer.replace("  ", " ")
                              .replace(" ,", ",")
                              .replace(" .", ".")
                              .replace(" !", "!")
                              .replace(" ?", "?")
                    )
                    print("📤 Yielding:", repr(cleaned))
                    yield cleaned
                    buffer = ""

            if buffer.strip():
                yield buffer

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# 🗂️ User's documents for chatbot
@router.get("/documents/mydocs")
def get_user_documents_for_chatbot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docs = db.query(Document).filter_by(user_id=current_user.id).all()
    return [
        {
            "id": doc.id,
            "name": doc.name,
            "domain": doc.domain,
            "created_at": doc.created_at.isoformat() if doc.created_at else "",
            "blob_url": doc.blob_url
        }
        for doc in docs
    ]


# 📜 Entire chat history
@router.get("/history")
def get_user_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = (
        db.query(ChatHistory)
        .filter_by(user_id=current_user.id)
        .order_by(ChatHistory.id.desc())
        .all()
    )
    return [
        {
            "question": item.question,
            "answer": item.answer,
            "domain": item.domain,
            "doc_id": item.doc_id
        }
        for item in history
    ]


# 📄 Chat history by document
@router.get("/history/{doc_name}")
def get_chat_history_by_document(
    doc_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter_by(user_id=current_user.id, name=doc_name).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    history = (
        db.query(ChatHistory)
        .filter_by(user_id=current_user.id, doc_id=doc.id)
        .order_by(ChatHistory.id.asc())
        .all()
    )

    return [
        {
            "question": item.question,
            "answer": item.answer
        }
        for item in history
    ]
