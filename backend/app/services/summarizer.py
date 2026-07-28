from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from app.services.llama_service import LlamaService


def _safe_json_loads(text: str) -> Dict[str, Any]:
    """
    LLM output may wrap JSON in markdown fences; try hard to recover.
    """
    if not text:
        return {}
    raw = text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)

    # If there is extra text around JSON, extract the first {...} block.
    if not raw.startswith("{"):
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            raw = m.group(0)
    try:
        return json.loads(raw)
    except Exception:
        return {}


def detect_equations(text: str, max_equations: int = 8) -> List[str]:
    if not text:
        return []
    equations: List[str] = []

    # LaTeX inline $...$ or $$...$$
    for m in re.finditer(r"\$\$[\s\S]{1,400}?\$\$|\$[^\n$]{1,200}\$", text):
        eq = m.group(0).strip()
        if eq not in equations:
            equations.append(eq)
        if len(equations) >= max_equations:
            return equations

    # Lines containing '=' or common math symbols
    symbols = ("=", "∑", "∫", "→", "≈", "≤", "≥", "λ", "μ", "σ", "α", "β", "γ")
    for line in text.splitlines():
        ln = line.strip()
        if len(ln) < 5 or len(ln) > 240:
            continue
        if any(s in ln for s in symbols):
            if ln not in equations:
                equations.append(ln)
        if len(equations) >= max_equations:
            break

    return equations[:max_equations]


def _normalize_key_concepts(items: Any) -> List[Dict[str, str]]:
    if not isinstance(items, list):
        return []

    concepts: List[Dict[str, str]] = []
    for idx, item in enumerate(items[:12], start=1):
        name = ""
        explanation = ""

        if isinstance(item, dict):
            name = str(item.get("name") or item.get("concept") or item.get("title") or "").strip()
            explanation = str(
                item.get("explanation") or item.get("description") or item.get("meaning") or ""
            ).strip()
        else:
            raw = str(item).strip()
            if ":" in raw:
                name, explanation = [part.strip() for part in raw.split(":", 1)]
            else:
                name = raw

        if name or explanation:
            concepts.append(
                {
                    "name": name or f"Concept {idx}",
                    "explanation": explanation,
                }
            )

    return concepts


def _chunk_for_llm(text: str, max_chars: int = 6000, overlap: int = 400) -> List[str]:
    """
    Chunk text before sending it to the hosted model so we can cover the entire PDF.
    Char-based chunking is simple and stable across different tokenizers.
    """
    if not text:
        return []
    max_chars = max(1000, int(max_chars))
    overlap = max(0, min(int(overlap), max_chars - 1))
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + max_chars)
        chunks.append(text[start:end].strip())
        if end == n:
            break
        start = max(0, end - overlap)
    return [c for c in chunks if c]


class Summarizer:
    def __init__(self) -> None:
        self._llm = LlamaService()

    def _summarize_chunk(self, chunk: str, idx: int, total: int) -> str:
        prompt = f"""
You are an expert research assistant.

Summarize this research paper chunk ({idx}/{total}) in clear plain text.
Focus on: problem, approach, key methods, experiments, results, and limitations.
If this chunk includes equations or algorithm steps, include a brief note.
Use a short paragraph followed by numbered points when useful.
Do not use Markdown headings, bold text, bullet symbols, asterisks, or blockquotes.

Chunk:
{chunk}
""".strip()
        return self._llm.generate_response(prompt)

    def summarize(self, paper_text: str) -> Dict[str, Any]:
        # 1) Chunk and summarize ALL chunks so we don't drop PDF content.
        chunks = _chunk_for_llm(paper_text, max_chars=6000, overlap=400)
        chunk_summaries: List[str] = []
        total = max(1, len(chunks))
        for i, ch in enumerate(chunks, start=1):
            chunk_summaries.append(self._summarize_chunk(ch, i, total))

        combined = "\n\n".join(
            [f"CHUNK {i}/{total} SUMMARY:\n{cs}" for i, cs in enumerate(chunk_summaries, start=1)]
        )

        # 2) Produce the final structured JSON summary from the combined chunk summaries.
        prompt = f"""
You are an expert research assistant.

Using ONLY the chunk summaries below (which together cover the full paper),
return ONLY valid JSON with this exact schema:
{{
  "summary": "complete multi-paragraph research paper summary",
  "key_concepts": [
    {{"name": "concept name", "explanation": "short clear explanation"}}
  ],
  "equations_detected": ["eq1", "eq2"]
}}

Rules:
- Ensure the JSON is parseable.
- summary should start with 1-2 explanatory paragraphs.
- After the paragraphs, include numbered points for objectives, method, results, limitations, and conclusion.
- Use plain text only. Do not use Markdown headings, bold text, bullet symbols, asterisks, or blockquotes.
- key_concepts should be 6-12 items, each with a concept name and short explanation.
- equations_detected can be empty (we will also detect heuristically).

Chunk summaries:
{combined}
""".strip()

        raw = self._llm.generate_response(prompt)
        data = _safe_json_loads(raw)
        if not data:
            # Fallback: provide something even if parsing fails.
            data = {
                "summary": "\n\n".join(chunk_summaries),
                "key_concepts": [],
                "equations_detected": [],
            }

        if not data.get("summary"):
            data["summary"] = data.get("detailed_summary", "") or data.get("short_summary", "")

        data["key_concepts"] = _normalize_key_concepts(data.get("key_concepts", []))

        # Backfill equations via heuristic detection if missing.
        if not isinstance(data.get("equations_detected"), list):
            data["equations_detected"] = []
        if not data["equations_detected"]:
            data["equations_detected"] = detect_equations(paper_text)

        return data

    def explain_equations(self, equations: List[str]) -> List[Dict[str, str]]:
        explanations: List[Dict[str, str]] = []
        for idx, eq in enumerate(equations[:8], start=1):
            prompt = f"""
You are an expert research assistant.

Return ONLY valid JSON with this exact schema:
{{
  "name": "short equation name",
  "explanation": "short plain text explanation"
}}

Rules:
- Name the equation based on what it represents in the paper.
- The explanation should be simple and 2-4 sentences.
- Do not use Markdown headings, bold text, bullet symbols, asterisks, or blockquotes.

Equation:
{eq}
""".strip()
            raw = self._llm.generate_response(prompt)
            parsed = _safe_json_loads(raw)
            explanations.append(
                {
                    "name": str(parsed.get("name") or f"Equation {idx}").strip(),
                    "equation": eq,
                    "explanation": str(parsed.get("explanation") or raw).strip(),
                }
            )
        return explanations

