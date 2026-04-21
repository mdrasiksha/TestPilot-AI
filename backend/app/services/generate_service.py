from app.services.ai_service import ai_service


def generate_from_user_story(user_story: str) -> str:
    return ai_service.generate(user_story)
