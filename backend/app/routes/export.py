from fastapi import APIRouter
from fastapi.responses import Response

from app.models.schema import ExportRequest
from app.services.export_service import export_service

router = APIRouter(tags=["export"])


@router.post("/export")
def export(payload: ExportRequest) -> Response:
    csv_content = export_service.to_csv_bytes(payload.test_cases)
    headers = {"Content-Disposition": 'attachment; filename="test_cases.csv"'}

    return Response(content=csv_content, media_type="text/csv", headers=headers)
