from fastapi import APIRouter

from app.models.schema import GenerateRequest, GenerateResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("", response_model=GenerateResponse)
def generate(payload: GenerateRequest) -> GenerateResponse:
    return GenerateResponse(content=ai_service.generate(payload.prompt))
