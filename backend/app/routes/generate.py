from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.services.ai_service import ai_service
from app.services.subscription_store import get_user, usage_store

router = APIRouter(tags=["generate"])

DAILY_LIMIT = 5


def get_today_date() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


@router.post("", summary="Generate test cases")
def generate(data: dict):
    try:
        print("Request received:", data)
        user_story = str(data.get("prompt") or data.get("user_story") or "").strip()
        user_id = str(data.get("user_id") or "").strip()

        if not user_id:
            user_id = "anonymous"

        if not user_story:
            raise HTTPException(status_code=400, detail="Missing prompt")

        db_user = get_user(user_id)
        now = datetime.utcnow()
        is_pro_user = bool(db_user and db_user.plan_expiry and db_user.plan_expiry > now)
        user_plan = "pro" if is_pro_user else "free"
        max_test_cases = 40 if is_pro_user else 10

        remaining: int | str = "unlimited"
        if not is_pro_user:
            today = get_today_date()
            user_data = usage_store.setdefault(user_id, {"date": today, "count": 0})

            if user_data["date"] != today:
                user_data["date"] = today
                user_data["count"] = 0

            if int(user_data["count"]) >= DAILY_LIMIT:
                return {
                    "error": "LIMIT_REACHED",
                    "remaining": 0,
                }

            user_data["count"] = int(user_data["count"]) + 1
            remaining = DAILY_LIMIT - int(user_data["count"])

        result = ai_service.generate_test_cases(user_story, max_cases=max_test_cases)

        if len(result) > max_test_cases:
            result = result[:max_test_cases]

        response_payload = {
            "data": result,
            "remaining": remaining,
            "plan": user_plan.upper(),
        }
        if not is_pro_user:
            response_payload["message"] = "Upgrade to Pro to unlock 40+ test cases"

        return response_payload

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
