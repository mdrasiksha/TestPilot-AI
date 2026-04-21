from fastapi import FastAPI

from app.core.config import get_settings
from app.routes.export import router as export_router
from app.routes.generate import router as generate_router

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(generate_router, prefix=settings.api_prefix)
app.include_router(export_router, prefix=settings.api_prefix)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
