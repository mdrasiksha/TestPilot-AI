from fastapi import APIRouter

from app.models.schema import (
    ExportResponse,
    GenerateRequest,
    GenerateResponse,
    UserStoryGenerateRequest,
)
from app.services.export_service import export_service
from app.services.generate_service import generate_from_user_story

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("", response_model=GenerateResponse)
def generate(payload: UserStoryGenerateRequest) -> GenerateResponse:
    return GenerateResponse(content=generate_from_user_story(payload.user_story))


@router.post("/export", response_model=ExportResponse)
def export(payload: GenerateRequest) -> ExportResponse:
    content = generate_from_user_story(payload.prompt)
    return ExportResponse(format="json", payload=export_service.to_json(content))
