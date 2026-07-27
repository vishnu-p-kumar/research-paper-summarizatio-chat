from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.db import ensure_database_schema
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.models import router as models_router
from app.routes.summarize import router as summarize_router
from app.routes.upload import router as upload_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Research Paper Summarizer + Chat (Gemini + PostgreSQL RAG)",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(auth_router, prefix="/api")
    app.include_router(upload_router)
    app.include_router(summarize_router)
    app.include_router(chat_router)
    app.include_router(models_router)

    @app.on_event("startup")
    async def startup():
        ensure_database_schema()

    @app.get("/health")
    async def health():
        return {"ok": True}

    return app


app = create_app()

