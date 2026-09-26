from fastapi import APIRouter
import logging

from app.core.request_context import request_id_context

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    logger.info(
        "Health endpoint called"
    )

    return {
        "status": "healthy",
        "request_id": request_id_context.get(),
    }