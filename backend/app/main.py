import os
import logging
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.utils.database import Base, engine, get_db
from app.schemas import ChatRequest, ChatResponse
from app.routes import documents, chatbot, summarize, translate, extract, download
from app.auth import routes as auth_routes
from app.auth.models import User
from app.models.chat import ChatHistory
from app.services.rag import (
    get_rag_chain,
    get_rag_streaming_chain,
    FastAPIStreamingCallbackHandler
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DocuSense AI Backend",
    description="...",
    version="1.0.0"
)

# ────────────────────────────────────────────────────────────────
# CORS  🔄  (only this block changed)
# ----------------------------------------------------------------
frontend_origin = os.getenv("ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_origin,
        "https://*.azurestaticapps.net"      # SWA wildcard
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ────────────────────────────────────────────────────────────────

# Routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(summarize.router, tags=["Summarization"])
app.include_router(translate.router, tags=["Translation"])
app.include_router(extract.router, prefix="/extract", tags=["Extraction"])
app.include_router(download.router, prefix="/export", tags=["Export & Download"])


@app.on_event("startup")
def preload_vectorstores():
    root = "vectorstores"
    os.makedirs(root, exist_ok=True)
    for base_dir, _, files in os.walk(root):
        if "index.faiss" in files:
            logger.info(f"✅ Pre-loaded vectorstore: {base_dir}")


@app.post("/chat", tags=["Chatbot"])
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=request.username).one()
    history = db.query(ChatHistory).filter_by(user_id=user.id, name=request.doc_name).one()
    chain = get_rag_chain(user.id, history.filename, user.domain)
    answer = chain.run(request.question)
    return JSONResponse({"answer": answer})


@app.post("/chat/stream", tags=["Chatbot"])
def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=request.username).one()
    history = db.query(ChatHistory).filter_by(user_id=user.id, name=request.doc_name).one()
    handler = FastAPIStreamingCallbackHandler()
    chain = get_rag_streaming_chain(user.id, history.filename, user.domain, handler)

    def event_generator():
        chain.run(request.question)
        while True:
            tok = handler.queue.get()
            if tok is None:
                break
            yield tok

    return StreamingResponse(event_generator(), media_type="text/plain")


# ────────────────────────────────────────────────────────────────
# Health-check  ✅  (changed to 200 + JSON body)
# ----------------------------------------------------------------
@app.get("/healthz", tags=["infra"])
def healthz():
    return {"status": "ok"}
# ────────────────────────────────────────────────────────────────
