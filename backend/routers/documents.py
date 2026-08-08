from fastapi import APIRouter, UploadFile, File
import tempfile
import os

from src.ingestion.pdf_loader import load_pdf
from src.ingestion.text_splitter import split_documents
from src.qa_engine import store_chunks

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp:

        temp.write(await file.read())

        temp_path = temp.name

    try:

        pages = load_pdf(
            temp_path,
            document_name=file.filename
        )

        chunks = split_documents(pages)

        store_chunks(chunks)

        return {
            "filename": file.filename,
            "chunks": len(chunks),
            "message": "Document indexed successfully."
        }

    finally:
        os.remove(temp_path)