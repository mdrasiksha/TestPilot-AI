import logging

from fastapi import APIRouter, HTTPException

from app.models.schema import GenerateRequest, GenerateResponse
from app.services.ai_service import ai_service

router = APIRouter(tags=["generate"])
logger = logging.getLogger(__name__)


@router.post("", response_model=GenerateResponse, summary="Generate test cases")
def generate(payload: GenerateRequest) -> GenerateResponse:
    try:
        prompt = (payload.prompt or "").strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="Missing prompt")

        logger.info("Generate endpoint called with prompt length=%s", len(prompt))
        test_cases = ai_service.generate_test_cases(prompt)
    except HTTPException:
        raise
    except ValueError as exc:
        logger.error("Generate validation error: %s", str(exc), exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error("Generate runtime error: %s", str(exc), exc_info=True)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Generate unexpected error: %s", str(exc), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    return GenerateResponse(test_cases=test_cases)
