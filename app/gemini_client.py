import json
import os
from typing import Any

from google import genai

from .prompts import PROMPT_TEMPLATE

MODEL_NAME = "gemini-1.5-flash"


class GeminiError(Exception):
    pass


def _extract_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise GeminiError("Gemini response was not valid JSON.") from exc


def _validate_minimum(data: dict[str, Any]) -> None:
    if "meeting_summary" not in data:
        raise GeminiError("Missing meeting_summary in Gemini response.")
    summary = data.get("meeting_summary", {}).get("summary")
    if not summary:
        raise GeminiError("Meeting summary is missing.")
    if "tasks" not in data or not isinstance(data.get("tasks"), list):
        raise GeminiError("Tasks list is missing or invalid.")


def _call_model(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not set.")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text or ""


def call_gemini_extract(meeting_payload: dict[str, Any]) -> dict[str, Any]:
    prompt = PROMPT_TEMPLATE.format(**meeting_payload)
    response_text = _call_model(prompt)
    try:
        data = _extract_json(response_text)
        _validate_minimum(data)
        return data
    except GeminiError:
        repair_prompt = (
            "Return valid JSON only; fix quotes/trailing commas; no extra text.\n\n"
            + response_text
        )
        repaired_text = _call_model(repair_prompt)
        data = _extract_json(repaired_text)
        _validate_minimum(data)
        return data
