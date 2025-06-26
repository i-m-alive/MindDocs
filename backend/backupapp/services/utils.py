import os
import fitz  # PyMuPDF
from io import BytesIO
from uuid import uuid4
from typing import List
from langchain_core.documents import Document as LangDoc
from PIL import Image
import requests
from fastapi import UploadFile
from pdf2image import convert_from_path, convert_from_bytes
from docx import Document as DocxDocument
from azure.storage.blob import BlobServiceClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import pytesseract
from urllib.parse import urlparse, unquote

# Configure Tesseract path (if needed on Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Azure Blob Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = "document-container"

UPLOAD_DIR = "uploaded_docs"

# ---------------------------------------
# ✅ General File Save Utility
# ---------------------------------------
def save_uploaded_file(uploaded_file: UploadFile, user_id: int) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = uploaded_file.filename.split(".")[-1]
    filename = f"{user_id}_{uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.file.read())
    return file_path

# ---------------------------------------
# ✅ Extract text from various formats
# ---------------------------------------
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        page_text = page.get_text()
        if not page_text.strip():
            # Try OCR
            images = convert_from_path(file_path)
            for image in images:
                text += pytesseract.image_to_string(image)
        else:
            text += page_text
    doc.close()
    return text

def extract_text_from_image(file_path: str) -> str:
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

def extract_text_from_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

# ---------------------------------------
# ✅ PDF Chunking from Local or Azure Blob
# ---------------------------------------


def load_and_chunk_pdf(file_path_or_url: str, chunk_size: int = 500) -> List[LangDoc]:
    """
    Load a PDF from Azure Blob Storage or local path, extract text (with OCR fallback),
    and split into LangChain-compatible document chunks.
    """
    try:
        full_text = ""
        blob_data = None

        # ✅ CASE 1: Azure Blob URL
        if file_path_or_url.startswith("https://"):
            parsed_url = urlparse(file_path_or_url)
            full_path = parsed_url.path.lstrip("/")  # remove leading slash

            if full_path.startswith(f"{AZURE_CONTAINER_NAME}/"):
                blob_name = full_path[len(f"{AZURE_CONTAINER_NAME}/"):]
            else:
                raise ValueError(f"Unexpected blob path format: {full_path}")

            print(f"[DEBUG] Azure blob path: {blob_name}")
            blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
            blob_client = blob_service.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)

            blob_data = blob_client.download_blob().readall()
            doc = fitz.open(stream=BytesIO(blob_data), filetype="pdf")

        # ✅ CASE 2: Local file
        else:
            if not os.path.exists(file_path_or_url):
                raise FileNotFoundError(f"File not found: {file_path_or_url}")
            doc = fitz.open(file_path_or_url)

        # ✅ Extract text from PDF pages
        for page in doc:
            text = page.get_text()
            if text.strip():
                full_text += text
        doc.close()

        # ✅ Fallback to OCR if no text found
        if not full_text.strip():
            print("[⚠️] No text found, using OCR fallback")
            if blob_data:
                images = convert_from_bytes(blob_data)
            else:
                with open(file_path_or_url, "rb") as f:
                    images = convert_from_bytes(f.read())

            for image in images:
                full_text += pytesseract.image_to_string(image)

        if not full_text.strip():
            raise ValueError("❗ No readable content found in PDF")

        # ✅ Split into LangChain chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "]
        )

        return splitter.split_documents([
            LangDoc(page_content=full_text, metadata={"source": file_path_or_url})
        ])

    except Exception as e:
        raise RuntimeError(f"❌ PDF processing failed: {e}")
