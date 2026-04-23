import json
import os
from typing import Any

from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VALID_PRIORITIES = {"High", "Medium", "Low"}
REQUIRED_FIELDS = {
    "id",
    "steps",
    "expected_result",
    "priority",
}


def extract_json(text: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads((text or "").strip())

        if isinstance(parsed, list):
            return parsed

        return []

    except Exception as e:
        print("JSON PARSE ERROR:", str(e))
        return []


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_case_structure(test_case: dict[str, Any]) -> bool:
    if not isinstance(test_case, dict):
        return False

    if not REQUIRED_FIELDS.issubset(test_case.keys()):
        return False

    if not _is_non_empty_string(test_case.get("id")):
        return False

    if test_case.get("priority") not in VALID_PRIORITIES:
        return False

    steps = test_case.get("steps")
    if not _is_non_empty_string(steps):
        return False

    if not _is_non_empty_string(test_case.get("expected_result")):
        return False

    return True


def _deduplicate_cases(test_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique_cases: list[dict[str, Any]] = []
    seen_signatures: set[tuple[str, str, str]] = set()

    for case in test_cases:
        steps = str(case.get("steps", "")).strip().lower()
        expected = str(case.get("expected_result", "")).strip().lower()
        priority = str(case.get("priority", "")).strip().lower()
        signature = (steps, expected, priority)

        if signature in seen_signatures:
            continue

        seen_signatures.add(signature)
        unique_cases.append(case)

    return unique_cases


def _normalize_and_validate_cases(test_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid_cases = [case for case in test_cases if _validate_case_structure(case)]
    deduplicated_cases = _deduplicate_cases(valid_cases)

    if len(deduplicated_cases) < 5:
        return []

    return deduplicated_cases


def generate_test_cases(user_story: str) -> list[dict[str, Any]]:
    try:
        if not user_story or not str(user_story).strip():
            return []

        if not os.getenv("OPENAI_API_KEY"):
            print("OPENAI ERROR: Missing OPENAI_API_KEY")
            return []

        prompt = f"""
You are a QA expert.

Convert the user story into test cases.

Return ONLY valid JSON in this format:

[
  {{
    "id": "TC001",
    "steps": "string",
    "expected_result": "string",
    "priority": "High | Medium | Low"
  }}
]

Rules:
- Generate at least 5 test cases
- Include positive, negative, and edge cases
- No explanation text
- No markdown
- No extra characters
- Output must be pure JSON only

User Story:
{user_story}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        content = response.choices[0].message.content if response.choices else "[]"

        print("RAW AI OUTPUT:", content)

        parsed = extract_json(content)
        if not isinstance(parsed, list):
            return []

        return _normalize_and_validate_cases(parsed)

    except Exception as e:
        print("OPENAI ERROR:", str(e))
        return []


class AIService:
    @staticmethod
    def generate_test_cases(user_story: str) -> list[dict[str, Any]]:
        return generate_test_cases(user_story)


ai_service = AIService()
