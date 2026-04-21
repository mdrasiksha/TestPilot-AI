from fastapi import APIRouter, HTTPException

from app.models.schema import JiraIssueRequest, JiraIssueResponse
from app.services.jira_service import jira_service

router = APIRouter(tags=["jira"])


@router.post("/issue", response_model=JiraIssueResponse, summary="Create Jira issue")
def create_issue(payload: JiraIssueRequest) -> JiraIssueResponse:
    try:
        issue = jira_service.create_issue(
            project_key=payload.project_key,
            summary=payload.summary,
            description=payload.description,
            issue_type=payload.issue_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return JiraIssueResponse(**issue)
