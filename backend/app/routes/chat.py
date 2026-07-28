from __future__ import annotations

import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.config import ENABLE_WEB_FALLBACK
from app.models.user import User
from app.services.llama_service import LlamaService
from app.services.rag_pipeline import rag_store
from app.services.web_search import web_search


router = APIRouter(prefix="", tags=["chat"])


class ChatRequest(BaseModel):
    doc_id: str
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = 5


_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "if",
    "then",
    "else",
    "when",
    "while",
    "what",
    "which",
    "who",
    "whom",
    "whose",
    "why",
    "how",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "do",
    "does",
    "did",
    "can",
    "could",
    "should",
    "would",
    "may",
    "might",
    "must",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "without",
    "as",
    "at",
    "by",
    "from",
    "about",
    "into",
    "over",
    "under",
    "between",
    "within",
    "across",
    "it",
    "this",
    "that",
    "these",
    "those",
    "i",
    "you",
    "we",
    "they",
    "he",
    "she",
    "them",
    "their",
    "our",
    "your",
    "my",
}


ANSWER_STYLE = """
Write the answer in clear plain text.
Start with a short explanatory paragraph.
Then, when useful, add numbered points using this format:
1. Point title: explanation
2. Point title: explanation
Use simple language and keep each point understandable.
Do not use Markdown headings, bold text, bullet symbols, asterisks, or blockquotes.
""".strip()


def _paper_mentions_query_terms(paper_text: str, query: str) -> bool:
    """
    Heuristic: if any meaningful query term appears in the PDF text, use RAG.
    Otherwise, answer normally (general LLM answer).
    """
    if not paper_text:
        return False
    tokens = re.findall(r"[A-Za-z0-9_\\-]{3,}", query.lower())
    terms = [t for t in tokens if t not in _STOPWORDS]
    if not terms:
        return True  # default to RAG for very short/ambiguous queries
    hay = paper_text.lower()
    return any(t in hay for t in terms[:12])


def _looks_like_insufficient_from_paper(answer: str) -> bool:
    if not answer:
        return True
    a = answer.lower()
    patterns = [
        "don't have enough information",
        "do not have enough information",
        "not in the context",
        "not in the provided context",
        "the paper does not",
        "the paper only mentions",
    ]
    return any(p in a for p in patterns)


@router.post("/chat")
async def chat(payload: ChatRequest, _user: User = Depends(get_current_user)):
    try:
        paper_text = rag_store.get_text(payload.doc_id, user_id=str(_user.id))
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown doc_id. Upload a paper first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load document: {e}")

    use_rag = _paper_mentions_query_terms(paper_text, payload.query)

    llm = LlamaService()

    if not use_rag:
        if ENABLE_WEB_FALLBACK:
            try:
                results = web_search(payload.query)
            except Exception:
                results = []

            web_context = "\n".join(
                [
                    f"- {r.get('title','')}\n  {r.get('snippet','')}\n  Source: {r.get('url','')}"
                    for r in results
                ]
            )
            prompt = f"""
You are a helpful assistant.

Answer the question using your general knowledge AND the web snippets below.
If web snippets are provided, prefer them and include 2-4 short citations as URLs.
{ANSWER_STYLE}

Web snippets:
{web_context or "No web snippets available."}

Question:
{payload.query}
""".strip()
            try:
                answer = llm.generate_response(prompt)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")
            return {
                "answer": answer,
                "sources": results,
                "mode": "web",
            }

        prompt = f"""
Answer using your general knowledge.
{ANSWER_STYLE}

Question:
{payload.query}
""".strip()
        try:
            answer = llm.generate_response(prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")
        return {"answer": answer, "sources": [], "mode": "general"}

    try:
        retrieved = rag_store.retrieve(payload.doc_id, payload.query, k=payload.top_k, user_id=str(_user.id))
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown doc_id. Upload a paper first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")

    context = "\n\n---\n\n".join([f"[Chunk {i}] {chunk}" for (i, _score, chunk) in retrieved])
    prompt = f"""
You are a careful assistant. Answer the user's question using ONLY the provided context.
If the answer is not in the context, say you don't have enough information from the paper.
{ANSWER_STYLE}

Context:
{context}

Question:
{payload.query}
""".strip()

    try:
        answer = llm.generate_response(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")

    # If the paper context doesn't answer it, fall back to web.
    if ENABLE_WEB_FALLBACK and _looks_like_insufficient_from_paper(answer):
        try:
            results = web_search(payload.query)
        except Exception:
            results = []
        web_context = "\n".join(
            [
                f"- {r.get('title','')}\n  {r.get('snippet','')}\n  Source: {r.get('url','')}"
                for r in results
            ]
        )
        prompt2 = f"""
You are a helpful assistant.

The paper context was insufficient. Answer using your general knowledge AND the web snippets below.
If web snippets are provided, prefer them and include 2-4 short citations as URLs.
{ANSWER_STYLE}

Web snippets:
{web_context or "No web snippets available."}

Question:
{payload.query}
""".strip()
        try:
            answer2 = llm.generate_response(prompt2)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")
        return {"answer": answer2, "sources": results, "mode": "web"}

    sources = [{"chunk_id": i, "score": score} for (i, score, _chunk) in retrieved]
    return {"answer": answer, "sources": sources, "mode": "rag"}

