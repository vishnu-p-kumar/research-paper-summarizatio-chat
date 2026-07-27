from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, HttpUrl

from app.auth.dependencies import get_current_user
from app.config import MAX_UPLOAD_MB
from app.models.user import User
from app.services.pdf_parser import extract_text_from_pdf_bytes
from app.services.rag_pipeline import rag_store
from app.services.url_scraper import scrape_text_from_url


router = APIRouter(prefix="/upload", tags=["upload"])


class UrlUploadRequest(BaseModel):
    url: HttpUrl


@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...), _user: User = Depends(get_current_user)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    data = await file.read()
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large (>{MAX_UPLOAD_MB}MB).")

    try:
        text = extract_text_from_pdf_bytes(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {e}")

    if not text:
        raise HTTPException(status_code=400, detail="No extractable text found in PDF.")

    try:
        doc_id = rag_store.create_doc(text, user_id=str(_user.id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index document: {e}")

    return {"doc_id": doc_id, "characters": len(text), "preview": text[:800]}


@router.post("/url")
async def upload_url(payload: UrlUploadRequest, _user: User = Depends(get_current_user)):
    try:
        text = scrape_text_from_url(str(payload.url))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {e}")

    if not text or len(text) < 500:
        raise HTTPException(
            status_code=400,
            detail="Could not extract enough text from the URL. Try uploading the PDF instead.",
        )

    try:
        doc_id = rag_store.create_doc(text, user_id=str(_user.id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index document: {e}")

    return {"doc_id": doc_id, "characters": len(text), "preview": text[:800]}

