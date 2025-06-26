from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.documents import Document
from app.models.extraction import DocumentExtraction
from app.services.utils import load_and_chunk_pdf
from app.services.rag import get_llm_by_domain

router = APIRouter()

@router.post("/extract")
def extract_keywords_from_document(
    user_id: int = Form(...),
    doc_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    🔍 Extracts structured keywords or fields from document using a domain-specific LLM.
    Saves extracted values to the database.

    Domains Supported:
    - retail: item list, quantity, pricing, totals
    - medical: patient details, diagnosis, prescriptions
    - finance: transactions, parties, dates
    - legal: case number, court, judgment summary
    - education: student name, subjects, grades

    Returns:
        JSON response with structured data.
    """

    # ✅ Step 1: Validate user-document ownership
    doc = db.query(Document).filter_by(id=doc_id, user_id=user_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found for this user.")

    # ✅ Step 2: Load document content
    try:
        chunks = load_and_chunk_pdf(doc.filename)
        full_text = "\n".join(chunk.page_content for chunk in chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load document: {e}")

    # ✅ Step 3: Build domain-specific prompt
    domain = doc.domain.lower()
    if domain == "retail":
        prompt = (
            "You are a smart AI assistant. Extract this receipt's structured data:\n"
            "- Items purchased (name, qty, unit price, total per item)\n"
            "- Subtotal, taxes, grand total\n- Purchase date, invoice number, store name\n\n"
            f"Document Text:\n{full_text}"
        )
    elif domain == "medical":
        prompt = (
            "Extract medical record fields:\n"
            "- Patient name, age, gender, diagnosis, medications, doctor name, date of visit\n\n"
            f"Document Text:\n{full_text}"
        )
    elif domain == "finance":
        prompt = (
            "Extract financial transaction data:\n"
            "- Payer, payee, transaction amount, currency, date, account number, narration\n\n"
            f"Document Text:\n{full_text}"
        )
    elif domain == "legal":
        prompt = (
            "Extract legal case details:\n"
            "- Case title, parties involved, court, judge, filing date, case number, judgment summary\n\n"
            f"Document Text:\n{full_text}"
        )
    elif domain == "education":
        prompt = (
            "Extract academic details:\n"
            "- Student name, courses or subjects, grades, exam dates, duration, institution name\n\n"
            f"Document Text:\n{full_text}"
        )
    else:
        prompt = (
            "Extract structured key-value data from this document. Include names, numbers, dates, headings, etc.\n\n"
            f"Document Text:\n{full_text}"
        )

    # ✅ Step 4: Call domain-specific LLM
    try:
        llm = get_llm_by_domain(domain)
        llm_output = llm.invoke(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM inference failed: {e}")

    # ✅ Step 5: Parse response as JSON/dict
    try:
        extracted_dict = eval(llm_output) if isinstance(llm_output, str) else llm_output
        if not isinstance(extracted_dict, dict):
            raise ValueError("LLM did not return a dictionary format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse LLM output: {e}")

    # ✅ Step 6: Save to DB
    try:
        record = DocumentExtraction(
            user_id=user_id,
            doc_id=doc_id,
            domain=domain,
            extracted_fields=extracted_dict,
            raw_text=full_text
        )
        db.add(record)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store in DB: {e}")

    # ✅ Step 7: Respond
    return {
        "status": "success",
        "doc_name": doc.name,
        "domain": domain,
        "extracted_fields": extracted_dict
    }
