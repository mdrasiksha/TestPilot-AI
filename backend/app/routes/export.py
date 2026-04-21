from fastapi import APIRouter, HTTPException

from app.models.schema import ExportRequest, ExportResponse
from app.services.ai_service import ai_service
from app.services.export_service import export_service

router = APIRouter(tags=["export"])


@router.post("", response_model=ExportResponse, summary="Generate and export JSON")
def export(payload: ExportRequest) -> ExportResponse:
    try:
        test_cases = ai_service.generate_test_cases(payload.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ExportResponse(format="json", payload=export_service.to_json(test_cases))
