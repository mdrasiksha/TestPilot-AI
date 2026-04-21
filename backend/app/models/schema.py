from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)


class GenerateResponse(BaseModel):
    content: str


class ExportResponse(BaseModel):
    format: str
    payload: str
