from fastapi import APIRouter, UploadFile, Form, File, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
import os, shutil, uuid
from azure.storage.blob import BlobServiceClient, ContentSettings
import logging
from app.utils.database import get_db
from app.models.documents import Document
from app.auth.models import User
from app.auth.dependencies import get_current_user  # ⬅️ JWT-based user validation

router = APIRouter()

# ✅ Local storage config
UPLOAD_FOLDER = "uploaded_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Azure config
AZURE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER")
blob_service = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
container_client = blob_service.get_container_client(AZURE_CONTAINER)


@router.post("/upload")
async def upload_documents(
    names: List[str] = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload multiple documents to local storage and Azure Blob.
    Store metadata in the database.
    """
    if len(files) != len(names):
        raise HTTPException(status_code=400, detail="Mismatch between files and names.")

    uploaded_doc_ids = []

    for i, file in enumerate(files):
        # ✅ Step 1: Generate secure filename
        file_id = str(uuid.uuid4())
        secure_filename = f"{file_id}_{file.filename}".replace(" ", "_")
        local_path = os.path.join(UPLOAD_FOLDER, secure_filename)
        blob_path = f"uploaded_docs/{secure_filename}"

        # ✅ Step 2: Read file content (important!)
        file_content = await file.read()

        # ✅ Step 3: Save locally
        with open(local_path, "wb") as f:
            f.write(file_content)

        # ✅ Step 4: Upload to Azure Blob using file_content
        try:
            blob_client = container_client.get_blob_client(blob_path)
            blob_client.upload_blob(
                data=file_content,
                overwrite=True,
                content_settings=ContentSettings(content_type="application/pdf")
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Azure upload failed: {e}")

        # ✅ Step 5: Construct Blob URL
        blob_url = f"https://{blob_service.account_name}.blob.core.windows.net/{AZURE_CONTAINER}/{blob_path}"

        # ✅ Step 6: Save metadata to DB
        doc = Document(
            user_id=current_user.id,
            domain=current_user.domain,
            name=names[i],
            filename=local_path,
            blob_url=blob_url
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        uploaded_doc_ids.append(doc.id)

    return {
        "uploaded_documents": uploaded_doc_ids,
        "domain": current_user.domain,
        "user": current_user.username
    }

logger = logging.getLogger(__name__)
@router.get("/documents/me")
def get_user_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch all documents uploaded by the current logged-in user.
    Returns metadata for document list and UI table.
    """
    try:
        if not current_user or not current_user.id:
            logger.error("🔒 No valid user in /documents/me route")
            raise HTTPException(status_code=401, detail="Unauthorized")

        docs = db.query(Document).filter_by(user_id=current_user.id).order_by(Document.created_at.desc()).all()
        logger.info(f"📄 Found {len(docs)} documents for user_id={current_user.id}")

        return [
            {
                "id": doc.id,
                "name": doc.name,
                "domain": doc.domain,
                "filename": doc.filename,
                "blob_url": doc.blob_url,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            }
            for doc in docs
        ]

    except Exception as e:
        logger.exception(f"❌ Error fetching documents for user {getattr(current_user, 'id', 'unknown')}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")
