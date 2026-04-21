from fastapi import APIRouter

from app.routes.export import router as export_router
from app.routes.generate import router as generate_router
from app.routes.health import router as health_router
from app.routes.jira import router as jira_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(generate_router, prefix="/generate")
api_router.include_router(export_router, prefix="/export")
api_router.include_router(jira_router, prefix="/jira")
