import json
import logging
import os
from typing import Any

from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

_REQUIRED_KEYS = ["id", "title", "steps", "expected", "priority"]
_VALID_PRIORITIES = {"high", "medium", "low"}


def extract_json(text: str) -> list[dict[str, Any]]:
    text = (text or "").strip()

    # remove markdown fences
    text = text.replace("```json", "").replace("```", "")

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON found")

    json_str = text[start : end + 1]
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON found in model response") from exc

    if not isinstance(data, list):
        raise ValueError("JSON root must be a list")

    seen_signatures: set[tuple[str, tuple[str, ...], str]] = set()
    normalized: list[dict[str, Any]] = []

    # validate structure and quality
    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Invalid test case at index {idx}: expected object")

        for key in _REQUIRED_KEYS:
            if key not in item:
                raise ValueError(f"Missing key: {key}")

        title = str(item["title"]).strip()
        expected = str(item["expected"]).strip()
        if not title or len(title.split()) < 3:
            raise ValueError(f"Invalid title for test case {idx}: must be meaningful")
        if not expected or len(expected.split()) < 4:
            raise ValueError(f"Invalid expected result for test case {idx}: too vague")

        steps = item["steps"]
        if not isinstance(steps, list) or not steps:
            raise ValueError(f"Invalid steps for test case {idx}: must be a non-empty list")

        cleaned_steps: list[str] = []
        for step in steps:
            step_text = str(step).strip()
            if len(step_text.split()) < 3:
                raise ValueError(f"Invalid step for test case {idx}: steps must be actionable")
            cleaned_steps.append(step_text)

        priority = str(item["priority"]).strip().capitalize()
        if priority.lower() not in _VALID_PRIORITIES:
            raise ValueError(f"Invalid priority for test case {idx}: {priority}")

        signature = (
            title.lower(),
            tuple(step.lower() for step in cleaned_steps),
            expected.lower(),
        )
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)

        normalized.append(
            {
                "id": str(item["id"]).strip() or f"TC_{idx:03d}",
                "title": title,
                "steps": cleaned_steps,
                "expected": expected,
                "priority": priority,
            }
        )

    if not normalized:
        raise ValueError("No valid test cases returned")

    return normalized


def generate_test_cases(user_story: str) -> list[dict[str, Any]]:
    if not user_story or not user_story.strip():
        raise ValueError("prompt must be a non-empty string.")

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY in environment.")

    try:
        prompt = f"""
You are a senior QA engineer.

Generate high-quality test cases.

STRICT RULES:
- Return ONLY JSON
- No explanation
- No text outside JSON

Format:
[
  {{
    "id": "TC_001",
    "title": "short meaningful title",
    "steps": ["step 1", "step 2"],
    "expected": "clear expected result",
    "priority": "High|Medium|Low"
  }}
]

Requirements:
- At least 3 functional test cases
- At least 2 negative test cases
- At least 2 edge cases
- Steps must be actionable and detailed
- Expected results must be precise and measurable
- Titles must be specific and meaningful
- Do not duplicate scenarios

User Story:
{user_story}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert QA engineer."},
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "test_cases",
                    "strict": True,
                    "schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "steps": {"type": "array", "items": {"type": "string"}},
                                "expected": {"type": "string"},
                                "priority": {"type": "string", "enum": ["High", "Medium", "Low"]},
                            },
                            "required": _REQUIRED_KEYS,
                        },
                        "minItems": 7,
                    },
                },
            },
            temperature=0.3,
        )

        content = response.choices[0].message.content or "[]"
        logger.info("OpenAI raw response content: %s", content)
        print("OPENAI RESPONSE CONTENT:", content)
        return extract_json(content)

    except ValueError as exc:
        error_message = f"Invalid model response: {str(exc)}"
        logger.error("OPENAI PARSING ERROR: %s", error_message, exc_info=True)
        print("OPENAI PARSING ERROR:", error_message)
        raise RuntimeError(error_message) from exc
    except Exception as exc:
        error_message = f"OpenAI request failed: {str(exc)}"
        logger.error("OPENAI ERROR: %s", error_message, exc_info=True)
        print("OPENAI ERROR:", error_message)
        raise RuntimeError(error_message) from exc


class AIService:
    @staticmethod
    def generate_test_cases(user_story: str) -> list[dict[str, Any]]:
        return generate_test_cases(user_story)


ai_service = AIService()
