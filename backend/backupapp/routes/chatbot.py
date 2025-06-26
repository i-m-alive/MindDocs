# app/routes/chatbot.py

import asyncio
import logging
from typing import List
import anyio
from fastapi import APIRouter, Depends, HTTPException, Form
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
    FastAPIStreamingCallbackHandler
)
from app.schemas import ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat_with_existing_documents(
    question: str = Form(...),
    doc_names: List[str] = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not doc_names:
        raise HTTPException(status_code=400, detail="Select at least one document.")

    doc = db.query(Document).filter_by(user_id=current_user.id, name=doc_names[0]).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    try:
        chain = get_rag_chain(
            user_id=str(current_user.id),
            file_path=doc.blob_url,  # ✅ Must be blob_url
            domain=doc.domain
        )
        formatted_q = f"""You are a friendly and helpful assistant. 
        Please read the user's question and respond naturally.

        User's question: {question}"""

        output = chain.invoke(formatted_q)

        answer = output["answer"]

        # Log chat history
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


# Streaming chat endpoint
@router.post("/chat/stream", response_class=StreamingResponse)
async def stream_chat_with_existing_documents(
    question: str = Form(...),
    doc_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ DEBUG LOGGING
    print("🟢 /chat/stream HIT")
    print(f"👤 Authenticated user ID: {current_user.id}")
    print(f"📄 Received doc_name: '{doc_name}'")
    print(f"❓ Received question: '{question}'")

    # ✅ Validate document existence
    doc = db.query(Document).filter_by(user_id=current_user.id, name=doc_name).first()

    if not doc:
        print("❌ Document not found for this user.")
        raise HTTPException(status_code=404, detail="Document not found.")

    handler = FastAPIStreamingCallbackHandler()

    try:
        # ✅ Initialize RAG chain with streaming callback
        chain = get_rag_streaming_chain(
            str(current_user.id),
            doc.blob_url,
            doc.domain,
            handler
        )
        print("✅ RAG chain initialized.")

    except Exception as e:
        logger.exception("❌ RAG stream chain init failed")
        raise HTTPException(status_code=500, detail="Streaming chain error.")

    # ✅ SSE token generator
    async def event_generator():
        async with anyio.create_task_group() as tg:
            # Run the LLM chain in background thread
            tg.start_soon(anyio.to_thread.run_sync, chain.invoke, question)

            async def stream_tokens():
                while True:
                    token = await handler.queue.get()
                    if token is None:
                        break
                    yield token

            # Yield tokens to client
            async for token in stream_tokens():
                yield token

    return StreamingResponse(event_generator(), media_type="text/plain")



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
            "blob_url": doc.blob_url  # if you're using Azure Blob Storage
        }
        for doc in docs
    ]

# Retrieve user's chat history
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
