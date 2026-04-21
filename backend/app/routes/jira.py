from fastapi import APIRouter, HTTPException

from app.services.jira_service import jira_service

router = APIRouter(prefix="/jira", tags=["jira"])


@router.get("/{issue_id}")
def get_jira_story(issue_id: str) -> dict[str, str]:
    try:
        story = jira_service.fetch_jira_story(issue_id)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"issue_id": issue_id, "story": story}
