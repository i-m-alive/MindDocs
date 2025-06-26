from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Literal

from app.utils.database import get_db
from app.models.documents import Document
from app.services.utils import load_and_chunk_pdf
from app.services.rag import get_llm_by_domain
from app.auth.dependencies import get_current_user
from app.auth.models import User

router = APIRouter()

@router.post("/translate")
async def translate_document(
    doc_name: str = Form(..., description="Name of the document to translate"),
    target_language: Literal[
        "English", "French", "German", "Spanish", "Hindi", "Chinese", "Arabic"
    ] = Form(..., description="Target language for translation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Translates an uploaded document using a domain-specific Groq LLM into the selected language.
    The document content is loaded from Azure Blob Storage based on the blob_url.
    """

    user_id = current_user.id

    # ✅ Step 1: Fetch document from DB and validate
    doc = db.query(Document).filter_by(user_id=user_id, name=doc_name).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_name}' not found for user.")

    # ✅ Step 2: Load and chunk document from Azure Blob Storage
    try:
        chunks = load_and_chunk_pdf(doc.blob_url)  # Uses Azure Blob logic internally
        if not chunks:
            raise ValueError("No readable content extracted from document.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load and parse document: {str(e)}")

    # ✅ Step 3: Load LLM for the user's document domain
    try:
        llm = get_llm_by_domain(doc.domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM initialization failed: {str(e)}")

    # ✅ Step 4: Translate each chunk individually
    translated_chunks = []
    for i, chunk in enumerate(chunks):
        chunk_text = chunk.page_content.strip()
        if not chunk_text:
            continue

        prompt = (
            f"You are a professional translator.\n"
            f"Translate the following document into {target_language}.\n"
            f"Preserve formatting, names, lists, and numbers.\n\n"
            f"--- Content Start ---\n{chunk_text}\n--- Content End ---"
        )

        try:
            result = llm.invoke(prompt)
            translated_chunks.append(f"--- Section {i+1} ---\n{result.content.strip()}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Translation failed at chunk {i+1}: {str(e)}")

    # ✅ Step 5: Join all parts and return translation
    final_translation = "\n\n".join(translated_chunks)

    return {
        "translation": final_translation,
        "language": target_language,
        "doc_name": doc.name,
        "domain": doc.domain,
        "total_chunks": len(translated_chunks)
    }
