from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)


class GenerateResponse(BaseModel):
    test_cases: list[dict[str, str]]


class ExportRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)


class ExportResponse(BaseModel):
    format: str
    payload: str


class JiraIssueRequest(BaseModel):
    project_key: str = Field(..., min_length=1, max_length=20)
    summary: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    issue_type: str = Field(default="Task", min_length=1, max_length=50)


class JiraIssueResponse(BaseModel):
    key: str
    url: str


class User(BaseModel):
    user_id: str
    email: str
    plan: str = "free"
