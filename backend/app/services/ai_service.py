import json
from typing import Any

from openai import OpenAI

from app.core.config import get_settings


TEST_CASE_SCHEMA = [
    {
        "id": "",
        "title": "",
        "steps": "",
        "expected": "",
        "priority": "",
    }
]


def _build_prompt(user_story: str) -> str:
    return (
        "You are a senior QA engineer. Generate software test cases from the user story.\\n"
        "Include functional test cases, negative test cases, and edge cases.\\n"
        "Return ONLY strict JSON (no markdown, no explanation) as an array using this shape:\\n"
        f"{json.dumps(TEST_CASE_SCHEMA, indent=2)}\\n"
        "Rules:\\n"
        "- id must be unique and concise (e.g., TC-001).\\n"
        "- steps must be a single string with ordered actions.\\n"
        "- expected must clearly describe expected behavior.\\n"
        "- priority must be one of: High, Medium, Low.\\n\\n"
        f"User story:\\n{user_story}"
    )


def _validate_test_cases(payload: Any) -> list[dict[str, str]]:
    if not isinstance(payload, list):
        raise ValueError("AI response must be a JSON array.")

    required_keys = {"id", "title", "steps", "expected", "priority"}
    valid_priorities = {"High", "Medium", "Low"}

    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"Test case at index {idx} is not a JSON object.")

        missing = required_keys - set(item.keys())
        if missing:
            raise ValueError(f"Test case at index {idx} is missing keys: {sorted(missing)}")

        for key in required_keys:
            if not isinstance(item[key], str):
                raise ValueError(f"Test case at index {idx} has non-string field: {key}")

        if item["priority"] not in valid_priorities:
            raise ValueError(
                f"Test case at index {idx} has invalid priority: {item['priority']}"
            )

    return payload


def generate_test_cases(user_story: str) -> list[dict[str, str]]:
    """Generate functional, negative, and edge test cases from a user story."""
    if not user_story or not user_story.strip():
        raise ValueError("user_story must be a non-empty string.")

    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY in environment.")

    client = OpenAI(api_key=settings.openai_api_key)

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=_build_prompt(user_story.strip()),
            max_output_tokens=2000,
        )
        content = response.output_text
    except Exception as exc:  # clean external API failure handling
        raise RuntimeError("Failed to generate test cases from OpenAI API.") from exc

    if not content:
        raise RuntimeError("OpenAI API returned an empty response.")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI API response was not valid JSON.") from exc

    return _validate_test_cases(parsed)


class AIService:
    def generate(self, prompt: str) -> str:
        """Backward-compatible wrapper returning a JSON string."""
        return json.dumps(generate_test_cases(prompt))


ai_service = AIService()
