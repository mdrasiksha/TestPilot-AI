from fastapi import APIRouter

from app.models.schema import ExportResponse, GenerateRequest, GenerateResponse
from app.services.ai_service import ai_service
from app.services.export_service import export_service

router = APIRouter(tags=["generate"])


@router.post("", response_model=GenerateResponse, summary="Generate content")
def generate(payload: GenerateRequest) -> GenerateResponse:
    return GenerateResponse(content=ai_service.generate(payload.prompt))


@router.post("/export", response_model=ExportResponse, summary="Generate and export JSON")
def export(payload: GenerateRequest) -> ExportResponse:
    content = ai_service.generate(payload.prompt)
    return ExportResponse(format="json", payload=export_service.to_json(content))
