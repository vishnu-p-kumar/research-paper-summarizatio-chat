from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from app.config import (
    GEMINI_API_KEY,
    GEMINI_BASE_URL,
    GEMINI_FALLBACK_MODELS,
    GEMINI_MAX_TOKENS,
    GEMINI_TEMPERATURE,
    MODEL_NAME,
)


class LlamaService:
    """
    Compatibility wrapper used by the existing routes.

    The implementation calls Google Gemini through the generateContent REST API.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_s: int = 120,
    ) -> None:
        self.base_url = (base_url or GEMINI_BASE_URL).rstrip("/")
        self.model_name = (model_name or MODEL_NAME or "gemini-3.6-flash").strip()
        self.timeout_s = timeout_s

    def generate_response(self, prompt: str, system: Optional[str] = None) -> str:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": GEMINI_TEMPERATURE,
                "maxOutputTokens": GEMINI_MAX_TOKENS,
            },
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        model_names = [self.model_name, *[m for m in GEMINI_FALLBACK_MODELS if m != self.model_name]]
        last_error: requests.HTTPError | None = None
        data: Dict[str, Any] | None = None

        for model_name in model_names:
            resp = requests.post(
                f"{self.base_url}/models/{model_name}:generateContent",
                headers={
                    "x-goog-api-key": GEMINI_API_KEY,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout_s,
            )
            if resp.status_code == 404:
                last_error = requests.HTTPError(
                    f"Gemini model '{model_name}' was not found or is unavailable for this API key.",
                    response=resp,
                )
                continue
            resp.raise_for_status()
            self.model_name = model_name
            data = resp.json()
            break

        if data is None:
            available_hint = ", ".join(model_names)
            raise RuntimeError(
                "No configured Gemini model is available. "
                f"Tried: {available_hint}. Use GET /models to see models available for your API key."
            ) from last_error

        candidates = data.get("candidates") or []
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts") or []
        return "".join(part.get("text", "") for part in parts).strip()

    def list_models(self) -> list[dict]:
        if not GEMINI_API_KEY:
            return [{"name": self.model_name, "provider": "Google Gemini", "configured": False}]

        resp = requests.get(
            f"{self.base_url}/models",
            headers={"x-goog-api-key": GEMINI_API_KEY},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        models = data.get("models") or []
        return [
            {
                "name": (model.get("name") or "").replace("models/", ""),
                "provider": "Google Gemini",
                "configured": (model.get("name") or "").endswith(self.model_name),
            }
            for model in models
            if "generateContent" in (model.get("supportedGenerationMethods") or [])
        ]
