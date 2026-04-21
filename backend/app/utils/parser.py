import json
from typing import Any


def normalize_prompt(prompt: str) -> str:
    return " ".join(prompt.strip().split())


def parse_json_payload(content: str) -> Any:
    return json.loads(content)
