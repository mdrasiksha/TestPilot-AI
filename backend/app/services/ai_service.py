import os
import traceback

from openai import OpenAI

from app.utils.parser import parse_json_payload


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_test_cases(user_story: str) -> list[dict[str, str]]:
    if not user_story or not user_story.strip():
        raise ValueError("prompt must be a non-empty string.")

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY in environment.")

    try:
        prompt = f"""
You are a QA expert.

Generate structured test cases in JSON format.

User Story:
{user_story}

Return JSON:
[
  {{
    "id": "TC_001",
    "title": "",
    "steps": "",
    "expected": "",
    "priority": "High/Medium/Low"
  }}
]
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior QA engineer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("OpenAI API returned an empty response.")

        payload = parse_json_payload(content)
        if not isinstance(payload, list):
            raise RuntimeError("OpenAI API response was not a JSON array.")

        return payload

    except Exception as e:
        print("OPENAI ERROR:", str(e))
        print(traceback.format_exc())
        raise RuntimeError(f"OpenAI Error: {str(e)}") from e


class AIService:
    @staticmethod
    def generate_test_cases(user_story: str) -> list[dict[str, str]]:
        return generate_test_cases(user_story)


ai_service = AIService()
