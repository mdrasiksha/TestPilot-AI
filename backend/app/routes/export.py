from typing import Any

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.services.export_service import generate_csv

router = APIRouter()


@router.post("/export")
def export(data: list[dict[str, Any]]):
    file_path = generate_csv(data)
    return FileResponse(file_path, filename="testcases.csv", media_type="text/csv")
