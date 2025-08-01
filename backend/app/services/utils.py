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
from urllib.parse import urlparse

import easyocr

# Initialize EasyOCR reader
ocr_reader = easyocr.Reader(['en'], gpu=False)

# Azure Blob Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = "user-docs"
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
            # OCR fallback
            images = convert_from_path(file_path)
            for image in images:
                result = ocr_reader.readtext(np.array(image), detail=0, paragraph=True)
                text += "\n".join(result)
        else:
            text += page_text
    doc.close()
    return text

def extract_text_from_image(file_path: str) -> str:
    image = Image.open(file_path)
    result = ocr_reader.readtext(np.array(image), detail=0, paragraph=True)
    return "\n".join(result)

def extract_text_from_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

# ---------------------------------------
# ✅ PDF Chunking from Local or Azure Blob
# ---------------------------------------
import numpy as np

def load_and_chunk_pdf(file_path_or_url: str, chunk_size: int = 500) -> List[LangDoc]:
    try:
        full_text = ""
        blob_data = None

        # ✅ PATCH 1: Fix .neet typo
        if ".windows.neet" in file_path_or_url:
            print("🔥 Fixing .neet typo")
            file_path_or_url = file_path_or_url.replace(".windows.neet", ".windows.net")

        # ✅ CASE 1: Azure Blob URL
        if file_path_or_url.startswith("https://"):
            parsed_url = urlparse(file_path_or_url)
            full_path = parsed_url.path.lstrip("/")
            path_parts = full_path.strip("/").split("/")

            container_name = path_parts[0].strip()
            blob_name = "/".join(path_parts[1:])

            print(f"📦 Parsed container = '{container_name}'")
            print(f"📄 Parsed blob = '{blob_name}'")

            blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
            container_client = blob_service.get_container_client(container_name)
            if not container_client.exists():
                raise RuntimeError(f"❌ Azure container '{container_name}' does not exist (parsed from: {file_path_or_url})")

            blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
            print("🔍 DEBUG BLOB ACCESS")
            print("🔗 Full URL =", file_path_or_url)

            blob_data = blob_client.download_blob().readall()
            doc = fitz.open(stream=BytesIO(blob_data), filetype="pdf")
            print("✅ Azure PDF loaded")

        # ✅ CASE 2: Local file
        else:
            if not os.path.exists(file_path_or_url):
                raise FileNotFoundError(f"File not found: {file_path_or_url}")
            doc = fitz.open(file_path_or_url)
            print("[DEBUG] Local PDF loaded =", file_path_or_url)

        for page in doc:
            text = page.get_text()
            if text.strip():
                full_text += text
        doc.close()

        # ✅ OCR fallback
        if not full_text.strip():
            print("[⚠️] No text found in PDF. Using OCR fallback.")
            if blob_data:
                images = convert_from_bytes(blob_data)
            else:
                with open(file_path_or_url, "rb") as f:
                    images = convert_from_bytes(f.read())

            for image in images:
                result = ocr_reader.readtext(np.array(image), detail=0, paragraph=True)
                full_text += "\n".join(result)

        if not full_text.strip():
            raise ValueError("❗ No readable content found in PDF.")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "]
        )

        chunks = splitter.split_documents([
            LangDoc(page_content=full_text, metadata={"source": file_path_or_url})
        ])

        print(f"✅ Chunked into {len(chunks)} pieces.")
        return chunks

    except Exception as e:
        raise RuntimeError(f"❌ PDF processing failed: {e}")
