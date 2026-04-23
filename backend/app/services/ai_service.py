import json
import os
from typing import Any

from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

REQUIRED_TYPE_MINIMUMS = {
    "Functional": 4,
    "Negative": 3,
    "Edge": 2,
    "Security": 1,
}

VALID_PRIORITIES = {"High", "Medium", "Low"}
REQUIRED_FIELDS = {
    "id",
    "title",
    "type",
    "priority",
    "preconditions",
    "steps",
    "expected",
}


def extract_json(text: str) -> list[dict[str, Any]]:
    try:
        text = (text or "").replace("```json", "").replace("```", "").strip()

        start = text.find("[")
        end = text.rfind("]")

        if start == -1 or end == -1 or end < start:
            return []

        json_str = text[start : end + 1]
        parsed = json.loads(json_str)

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

    if not _is_non_empty_string(test_case.get("title")):
        return False

    if test_case.get("type") not in REQUIRED_TYPE_MINIMUMS:
        return False

    if test_case.get("priority") not in VALID_PRIORITIES:
        return False

    preconditions = test_case.get("preconditions")
    if not isinstance(preconditions, list) or not preconditions:
        return False
    if not all(_is_non_empty_string(item) for item in preconditions):
        return False

    steps = test_case.get("steps")
    if not isinstance(steps, list) or not steps:
        return False
    if not all(_is_non_empty_string(step) for step in steps):
        return False

    if not _is_non_empty_string(test_case.get("expected")):
        return False

    return True


def _deduplicate_cases(test_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique_cases: list[dict[str, Any]] = []
    seen_signatures: set[tuple[str, str, str, str]] = set()

    for case in test_cases:
        title = case.get("title", "").strip().lower()
        case_type = case.get("type", "").strip().lower()
        expected = case.get("expected", "").strip().lower()
        steps = " | ".join(str(step).strip().lower() for step in case.get("steps", []))

        signature = (title, case_type, steps, expected)

        if signature in seen_signatures:
            continue

        seen_signatures.add(signature)
        unique_cases.append(case)

    return unique_cases


def _meets_minimum_coverage(test_cases: list[dict[str, Any]]) -> bool:
    counts = {key: 0 for key in REQUIRED_TYPE_MINIMUMS}

    for case in test_cases:
        case_type = case.get("type")
        if case_type in counts:
            counts[case_type] += 1

    return all(counts[case_type] >= minimum for case_type, minimum in REQUIRED_TYPE_MINIMUMS.items())


def _normalize_and_validate_cases(test_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid_cases = [case for case in test_cases if _validate_case_structure(case)]
    deduplicated_cases = _deduplicate_cases(valid_cases)

    if len(deduplicated_cases) < sum(REQUIRED_TYPE_MINIMUMS.values()):
        return []

    if not _meets_minimum_coverage(deduplicated_cases):
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
You are a senior QA architect.

Generate enterprise-level test cases.

STRICT RULES:
- Return ONLY JSON
- No explanation
- No extra text

Output format:
[
  {{
    "id": "TC_001",
    "title": "Clear and meaningful test case title",
    "type": "Functional | Negative | Edge | Security",
    "priority": "High | Medium | Low",
    "preconditions": ["state before test"],
    "steps": ["step 1", "step 2"],
    "expected": "clear expected result"
  }}
]

Coverage minimums:
- Functional: 4
- Negative: 3
- Edge: 2
- Security: 1

Include:
- functional cases
- negative cases
- edge cases
- security scenarios
- validation cases
- error handling
- boundary conditions
- invalid inputs
- system failures

Ensure:
- realistic scenarios
- production-level coverage
- no duplicates
- executable steps
- precise expected results

Domain awareness:
- Authentication: invalid credentials, account lock, password rules, session handling
- Payments: failure scenarios, timeout, duplicate transactions

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
