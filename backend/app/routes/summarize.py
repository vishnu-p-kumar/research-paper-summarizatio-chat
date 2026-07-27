from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.rag_pipeline import rag_store
from app.services.summarizer import Summarizer


router = APIRouter(prefix="", tags=["summarize"])


class SummarizeRequest(BaseModel):
    doc_id: str


@router.post("/summarize")
async def summarize(payload: SummarizeRequest, _user: User = Depends(get_current_user)):
    try:
        text = rag_store.get_text(payload.doc_id, user_id=str(_user.id))
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown doc_id. Upload a paper first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        s = Summarizer()
        data = s.summarize(text)
        equation_explanations = s.explain_equations(data.get("equations_detected", []))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")

    return {
        "summary": data.get("summary", ""),
        "detailed_summary": data.get("summary", ""),
        "key_concepts": data.get("key_concepts", []),
        "equations": equation_explanations,
    }

