from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.documents import Document
from app.models.summary import SummaryHistory
from app.services.utils import load_and_chunk_pdf
from app.services.rag import get_llm_by_domain
from app.auth.dependencies import get_current_user
from app.auth.models import User

router = APIRouter()

@router.post("/summarize")
async def summarize_document(
    doc_name: str = Form(..., description="Name of the document to summarize"),
    ratio: float = Form(0.3, gt=0.05, lt=1.0, description="Compression ratio (0.05 - 0.95)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to summarize a document uploaded by the user.
    The document is fetched from Azure Blob Storage using its blob_url.
    A domain-specific LLM is used to generate summaries.
    """

    user_id = current_user.id

    # ✅ Step 1: Fetch document record by name and user
    doc = db.query(Document).filter_by(user_id=user_id, name=doc_name).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_name}' not found for user.")

    # ✅ Step 2: Load and chunk the document from Azure Blob
    try:
        chunks = load_and_chunk_pdf(doc.blob_url)  # Uses blob_url internally
        if not chunks:
            raise ValueError("No readable content extracted from document.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read and chunk document: {str(e)}")

    # ✅ Step 3: Compute word statistics
    total_words = sum(len(chunk.page_content.split()) for chunk in chunks)
    target_words = max(100, int(total_words * ratio))

    # ✅ Step 4: Load domain-specific LLM
    try:
        llm = get_llm_by_domain(doc.domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load LLM for domain '{doc.domain}': {str(e)}")

    # ✅ Step 5: Summarize each chunk
    partial_summaries = []
    for i, chunk in enumerate(chunks):
        chunk_words = max(30, int(len(chunk.page_content.split()) * ratio))
        prompt = (
            f"Summarize the following text in about {chunk_words} words:\n\n"
            f"{chunk.page_content}"
        )
        try:
            result = llm.invoke(prompt)
            partial_summaries.append(result.content.strip())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chunk {i+1} summarization failed: {str(e)}")

    # ✅ Step 6: Merge all partial summaries into one coherent summary
    combined_summary = "\n".join(partial_summaries)
    final_prompt = (
        f"Merge the following summaries into one coherent paragraph, "
        f"approximately {target_words} words:\n\n{combined_summary}"
    )
    try:
        final_summary = llm.invoke(final_prompt).content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Final summary generation failed: {str(e)}")

    # ✅ Step 7: Save summary history to the database (optional logging)
    try:
        record = SummaryHistory(
            user_id=user_id,
            doc_id=doc.id,
            summary_text=final_summary,
            original_word_count=total_words,
            summary_word_count=len(final_summary.split()),
            compression_ratio=f"{ratio:.2f}"
        )
        db.add(record)
        db.commit()
    except Exception as e:
        print(f"[⚠️] Failed to log summary history: {str(e)}")  # Non-blocking

    # ✅ Step 8: Return structured response
    return {
        "summary": final_summary,
        "doc_name": doc.name,
        "domain": doc.domain,
        "original_word_count": total_words,
        "summary_word_count": len(final_summary.split()),
        "compression_ratio": f"{ratio:.2f}"
    }
