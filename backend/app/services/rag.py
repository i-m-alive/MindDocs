import os
import asyncio
import logging
from typing import Any, Optional, Dict
from dotenv import load_dotenv

from app.services.utils import load_and_chunk_pdf
from app.utils.azure_blob_utils import get_blob_url_from_filename
from sqlalchemy.exc import OperationalError
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks.base import BaseCallbackHandler
from langchain.embeddings import HuggingFaceEmbeddings  # ✅ Use this for preloaded model
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer  # ✅ Preload model
from duckduckgo_search import DDGS

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VECTOR_FOLDER = "vectorstores"
os.makedirs(VECTOR_FOLDER, exist_ok=True)

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
DEFAULT_GROQ_MODEL = "llama3-70b-8192"

domain_prompts: Dict[str, str] = {
    "medical": "You are a professional medical assistant.",
    "retail": "You are a smart retail assistant.",
    "finance": "You are an expert financial analyst.",
    "legal": "You are a helpful legal assistant.",
    "education": "You are an intelligent teaching assistant.",
    "default": "You are a helpful assistant.",
}

user_memory: Dict[str, ConversationBufferMemory] = {}

def get_llm_by_domain(domain: str, stream=False, handler=None) -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("🔴 Missing GROQ_API_KEY in environment variables")

    persona = domain_prompts.get(domain.lower(), domain_prompts["default"])
    logger.info(f"✅ Using persona for domain '{domain}': {persona}")
    logger.info(f"🔐 First 8 of key: {api_key[:8]}...")

    llm = ChatGroq(
        model=DEFAULT_GROQ_MODEL,
        api_key=api_key,
        base_url="https://api.groq.com",
        temperature=0.9,
        streaming=stream,
        callbacks=[handler] if stream and handler else None
    )
    return llm

def get_vectorstore_path(user_id: str, file_path: str) -> str:
    fname = os.path.basename(file_path).replace(" ", "_").replace(".", "_")
    return os.path.join(VECTOR_FOLDER, f"{user_id}_{fname}")

def build_rag_chain(
    user_id: str,
    file_path: str,
    domain: str,
    stream: bool = False,
    handler: Optional[BaseCallbackHandler] = None
) -> ConversationalRetrievalChain:
    try:
        from urllib.parse import urlparse
        logger.info(f"🔧 Building RAG chain for user: {user_id}, domain: {domain}, stream: {stream}")

        embeddings = HuggingFaceEmbeddings(client=embedding_model)
        blob_name = os.path.basename(urlparse(file_path).path).replace(".", "_").replace(" ", "_")
        vs_folder = os.path.join(VECTOR_FOLDER, f"{user_id}_{blob_name}")
        os.makedirs(vs_folder, exist_ok=True)
        index_path = os.path.join(vs_folder, "index.faiss")

        if os.path.exists(index_path):
            logger.info(f"🔁 Reloading FAISS index from {vs_folder}")
            vs = FAISS.load_local(vs_folder, embeddings, allow_dangerous_deserialization=True)
        else:
            logger.info(f"⚙️ Creating FAISS index from blob: {file_path}")
            docs = load_and_chunk_pdf(file_path)
            if not docs:
                print("❌ No chunks generated — document empty or OCR failed")
            else:
                print("📃 First chunk preview:", docs[0].page_content[:300])
            vs = FAISS.from_documents(docs, embeddings)
            vs.save_local(vs_folder)

        retriever = vs.as_retriever()
        mem_key = f"{user_id}:{file_path}"
        memory = user_memory.get(mem_key)
        if not memory:
            logger.info(f"🧠 Creating memory buffer for: {mem_key}")
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            user_memory[mem_key] = memory

        llm = get_llm_by_domain(domain, stream=stream, handler=handler)

        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            output_key="answer"
        )
        chain.memory.output_key = "answer"
        logger.info("✅ RAG chain built successfully")
        return chain

    except OperationalError as db_err:
        logger.exception("Database/faiss access issue")
        raise RuntimeError("FAISS/database access failed") from db_err
    except ImportError as imp_err:
        logger.exception("Missing FAISS or LangChain dependency")
        raise RuntimeError("Install faiss-cpu and required LangChain packages") from imp_err
    except Exception as exc:
        logger.exception("Unexpected error building RAG chain")
        raise RuntimeError("Unexpected error in building RAG chain") from exc

def get_rag_chain(user_id: str, file_path: str, domain: str) -> ConversationalRetrievalChain:
    if not file_path.startswith("http"):
        file_path = get_blob_url_from_filename(file_path)
        print(f"🔗 Converted filename to blob URL: {file_path}")

    print("✅ file_path passed to build_rag_chain =", file_path)
    return build_rag_chain(user_id=user_id, file_path=file_path, domain=domain, stream=False, handler=None)

def get_rag_streaming_chain(
    user_id: str,
    blob_url: str,
    domain: str,
    stream_handler: BaseCallbackHandler
):
    if not blob_url.startswith("http"):
        blob_url = get_blob_url_from_filename(blob_url)
        print(f"🔗 Converted filename to blob URL: {blob_url}")

    rag_chain = build_rag_chain(user_id, blob_url, domain, stream=True, handler=stream_handler)
    llm = get_llm_by_domain(domain, stream=True, handler=stream_handler)
    search_tool = None  # Optional: replace this with actual tool if needed

    return rag_chain, search_tool, llm


def duckduckgo_search(query: str, num_results: int = 5) -> str:
    results_text = ""
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=num_results)
        for result in results:
            title = result.get("title", "")
            href = result.get("href", "")
            body = result.get("body", "")
            results_text += f"{title}\n{body}\n{href}\n\n"
    return results_text.strip()

class FastAPIStreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.queue = asyncio.Queue()

    async def on_llm_new_token(self, token: str, **kwargs):
        print("🧠 Token:", repr(token))
        if token:
            await self.queue.put(token)

    async def on_llm_end(self, *args, **kwargs):
        print("✅ on_llm_end triggered")
        await self.queue.put(None)
