import json
import os
import re
from typing import Any

from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VALID_PRIORITIES = {"High", "Medium", "Low"}
REQUIRED_FIELDS = {
    "id",
    "title",
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

    title = test_case.get("title")
    if not _is_non_empty_string(title):
        return False
    if str(title).strip().lower() == "untitled test case":
        return False

    if test_case.get("priority") not in VALID_PRIORITIES:
        return False

    steps = test_case.get("steps")
    if not isinstance(steps, list):
        return False
    if len(steps) < 3:
        return False
    if not all(_is_non_empty_string(step) for step in steps):
        return False

    if not _is_non_empty_string(test_case.get("expected_result")):
        return False

    return True


def _sanitize_step(step: Any) -> str:
    text = str(step or "").strip()
    if not text:
        return ""

    text = re.sub(r"^\s*[•\-\*]+\s*", "", text)
    text = re.sub(r"^\s*step\s*\d+\s*[:.)-]?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^\s*\d+\s*[:.)-]\s*", "", text)
    return text.strip()


def _normalize_steps(steps: Any) -> list[str]:
    if isinstance(steps, list):
        candidates = steps
    elif isinstance(steps, str):
        candidates = re.split(r"(?:\r?\n|;)", steps)
    else:
        return []

    normalized: list[str] = []
    for raw_step in candidates:
        cleaned = _sanitize_step(raw_step)
        if cleaned:
            normalized.append(cleaned)

    return normalized


def _normalize_case(case: dict[str, Any], index: int) -> dict[str, Any]:
    title = str(case.get("title") or "").strip()
    if not title or title.lower() == "untitled test case":
        title = f"Generated test case {index + 1}"

    expected_result = str(
        case.get("expected_result") or case.get("expected") or case.get("result") or ""
    ).strip()
    priority = str(case.get("priority") or "Medium").strip().title()
    if priority not in VALID_PRIORITIES:
        priority = "Medium"

    return {
        "id": str(case.get("id") or f"TC{index + 1:03d}").strip(),
        "title": title,
        "steps": _normalize_steps(case.get("steps")),
        "expected_result": expected_result,
        "priority": priority,
    }


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
    normalized_cases = [_normalize_case(case, i) for i, case in enumerate(test_cases)]
    valid_cases = [case for case in normalized_cases if _validate_case_structure(case)]
    deduplicated_cases = _deduplicate_cases(valid_cases)

    return deduplicated_cases


def build_prompt(requirement: str, max_cases: int) -> str:
    return f"""
You are a senior QA engineer.

Generate test cases for:
{requirement}

RULES:
- Generate AT LEAST {max_cases} test cases
- Do not stop early
- Expand deeply

Cover:
- Functional
- Negative
- Edge cases
- Boundary
- Security
- Performance

Output MUST be valid JSON only in this schema:
[
  {{
    \"id\": \"TC001\",
    \"title\": \"string\",
    \"steps\": [\"step 1\", \"step 2\", \"step 3\"],
    \"expected_result\": \"string\",
    \"priority\": \"High | Medium | Low\"
  }}
]

Keep output concise but complete.
"""


def generate_test_cases(user_story: str, max_cases: int = 10) -> list[dict[str, Any]]:
    try:
        if not user_story or not str(user_story).strip():
            return []

        if not os.getenv("OPENAI_API_KEY"):
            print("OPENAI ERROR: Missing OPENAI_API_KEY")
            return []

        prompt = build_prompt(user_story, max_cases)

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
    def generate_test_cases(user_story: str, max_cases: int = 10) -> list[dict[str, Any]]:
        return generate_test_cases(user_story, max_cases=max_cases)


ai_service = AIService()
