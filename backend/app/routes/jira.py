from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.jira_service import get_jira_issue, push_test_cases

router = APIRouter(tags=["jira"])


class JiraPushRequest(BaseModel):
    project_key: str = Field(..., min_length=1, max_length=20)
    test_cases: list[dict[str, Any]] = Field(default_factory=list)


@router.get("/jira/{issue_key}")
def fetch_jira_issue(issue_key: str) -> dict[str, str]:
    try:
        user_story = get_jira_issue(issue_key)
        return {"user_story": user_story}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/jira/push")
def push_jira_test_cases(payload: JiraPushRequest) -> dict[str, int]:
    try:
        created_issues = push_test_cases(payload.project_key, payload.test_cases)
        return {"created": len(created_issues)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
