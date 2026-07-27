from __future__ import annotations

import fitz  # PyMuPDF

from app.utils.text_cleaner import clean_text


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    if not pdf_bytes:
        return ""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    parts: list[str] = []
    for page in doc:
        parts.append(page.get_text("text"))
    doc.close()
    return clean_text("\n".join(parts))

