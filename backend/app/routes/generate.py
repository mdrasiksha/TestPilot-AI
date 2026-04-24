from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.services.ai_service import ai_service

router = APIRouter(tags=["generate"])

DAILY_LIMIT = 10
usage_store: dict[str, dict[str, int | str]] = {}


def get_today_date() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


@router.post("", summary="Generate test cases")
def generate(data: dict):
    try:
        user_story = str(data.get("prompt") or data.get("user_story") or "").strip()
        user_id = str(data.get("user_id") or "").strip()

        if not user_id:
            user_id = "anonymous"

        today = get_today_date()
        user_data = usage_store.setdefault(user_id, {"date": today, "count": 0})

        if user_data["date"] != today:
            user_data["date"] = today
            user_data["count"] = 0

        remaining_before = DAILY_LIMIT - int(user_data["count"])
        if remaining_before <= 0:
            return {
                "error": "LIMIT_REACHED",
                "message": "Daily limit reached",
                "data": [],
                "remaining": 0,
            }

        if not user_story:
            raise HTTPException(status_code=400, detail="Missing prompt")

        user_data["count"] = int(user_data["count"]) + 1
        result = ai_service.generate_test_cases(user_story)
        remaining = max(0, DAILY_LIMIT - int(user_data["count"]))

        return {"data": result, "remaining": remaining}

    except HTTPException as exc:
        print("API ERROR:", str(exc.detail))
        remaining = DAILY_LIMIT
        user_id = str(data.get("user_id") or "anonymous").strip() or "anonymous"
        user_data = usage_store.get(user_id)
        if user_data:
            remaining = max(0, DAILY_LIMIT - int(user_data.get("count", 0)))
        return {"error": str(exc.detail), "data": [], "remaining": remaining}
    except Exception as e:
        print("API ERROR:", str(e))
        remaining = DAILY_LIMIT
        user_id = str(data.get("user_id") or "anonymous").strip() or "anonymous"
        user_data = usage_store.get(user_id)
        if user_data:
            remaining = max(0, DAILY_LIMIT - int(user_data.get("count", 0)))
        return {"error": str(e), "data": [], "remaining": remaining}
