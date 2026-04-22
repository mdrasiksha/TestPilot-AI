from fastapi import APIRouter, HTTPException

from app.services.ai_service import ai_service

router = APIRouter(tags=["generate"])


@router.post("", summary="Generate test cases")
def generate(data: dict):
    try:
        user_story = str(data.get("prompt", "")).strip()

        if not user_story:
            raise HTTPException(status_code=400, detail="Missing prompt")

        result = ai_service.generate_test_cases(user_story)

        return {"data": result}

    except HTTPException as exc:
        print("API ERROR:", str(exc.detail))
        return {"error": str(exc.detail), "data": []}
    except Exception as e:
        print("API ERROR:", str(e))
        return {"error": str(e), "data": []}
