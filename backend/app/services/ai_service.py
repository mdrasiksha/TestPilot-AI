import json
import os
from typing import Any

from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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


def generate_test_cases(user_story: str) -> list[dict[str, Any]]:
    try:
        if not user_story or not str(user_story).strip():
            return []

        if not os.getenv("OPENAI_API_KEY"):
            print("OPENAI ERROR: Missing OPENAI_API_KEY")
            return []

        prompt = f"""
Return ONLY JSON array.

Format:
[
  {{
    "id": "TC_001",
    "title": "",
    "steps": ["step 1"],
    "expected": "",
    "priority": "High|Medium|Low"
  }}
]

User Story:
{user_story}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        content = response.choices[0].message.content if response.choices else "[]"

        print("RAW AI OUTPUT:", content)

        parsed = extract_json(content)

        return parsed if isinstance(parsed, list) else []

    except Exception as e:
        print("OPENAI ERROR:", str(e))
        return []


class AIService:
    @staticmethod
    def generate_test_cases(user_story: str) -> list[dict[str, Any]]:
        return generate_test_cases(user_story)


ai_service = AIService()
