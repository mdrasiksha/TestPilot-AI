from app.utils.parser import normalize_prompt


class AIService:
    def generate(self, prompt: str) -> str:
        clean_prompt = normalize_prompt(prompt)
        return f"Generated response for: {clean_prompt}"


ai_service = AIService()
