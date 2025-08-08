"""
Intent analysis using Gemini to extract request, tone, context, and pieces.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except Exception:  # pragma: no cover - environment dependent
    GEMINI_AVAILABLE = False


INTENT_PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "docs",
    "specs",
    "leadership_button",
    "intent_prompt.md",
)


class IntentAnalyzer:
    """Runs a lightweight intent analysis pass before main prompt generation."""

    def __init__(self, model: str = "gemini-1.5-flash", temperature: float = 0.2):
        if not GEMINI_AVAILABLE:
            raise RuntimeError(
                "google-generativeai not installed. Install with: pip install google-generativeai"
            )
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY missing in environment. Set it in your .env file."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.temperature = temperature

        # Preload prompt
        try:
            with open(INTENT_PROMPT_PATH, "r", encoding="utf-8") as f:
                self.intent_prompt_template = f.read()
        except Exception:
            # Minimal fallback template
            self.intent_prompt_template = (
                "Extract intent as JSON with keys request, tone, context, pieces "
                "from: {utterance}"
            )

    def analyze(self, utterance: str) -> Dict[str, Any]:
        """Return dict with keys: request, tone, context, pieces (list)."""
        prompt = self.intent_prompt_template.replace("{utterance}", utterance)
        logging.info("🔎 Running intent analysis")
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": 200,
                },
                request_options={"timeout": 20},
            )
            text = self._extract_text(response)
            data = self._parse_json(text)
            logging.info("🧭 Intent JSON: %s", json.dumps(data, ensure_ascii=False))
            return self._normalize(data)
        except Exception as exc:
            logging.warning("Intent analysis failed: %s", exc)
            return {
                "request": "advice",
                "tone": "regular",
                "context": "",
                "pieces": [],
            }

    def _extract_text(self, response: Any) -> str:
        try:
            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text or "{}"
        except Exception:
            pass
        return "{}"

    def _parse_json(self, text: str) -> Dict[str, Any]:
        # Remove code fences if present
        cleaned = re.sub(r"```[a-zA-Z]*\n?|```", "", text).strip()
        # Try direct parse
        try:
            return json.loads(cleaned)
        except Exception:
            # Try to find first JSON object
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError("No valid JSON in LLM response")

    def _normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = str(data.get("request", "advice")).lower().strip()
        if request not in {"story", "advice", "specific_story"}:
            request = "advice"
        tone = str(data.get("tone", "regular")).lower().strip().replace(" ", "_")
        context = str(data.get("context", "")).strip()
        pieces_raw = data.get("pieces", [])
        pieces: List[Dict[str, str]] = []
        if isinstance(pieces_raw, list):
            for item in pieces_raw:
                if isinstance(item, dict):
                    name = str(item.get("name", "")).strip()
                    desc = str(item.get("description", "")).strip()
                    if name:
                        pieces.append({"name": name, "description": desc})
        return {
            "request": request,
            "tone": tone or "regular",
            "context": context[:160],
            "pieces": pieces,
        }
