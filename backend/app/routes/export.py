from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.export_service import generate_csv, generate_excel

router = APIRouter()


@router.post("/export")
def export(data: Any):
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="Expected list of test cases")

    file_path = generate_csv(data)
    return FileResponse(file_path, filename="testcases.csv", media_type="text/csv")


@router.post("/export-excel")
def export_excel(data: Any):
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="Expected list of test cases")

    file_path = generate_excel(data)
    return FileResponse(
        file_path,
        filename="testcases.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
