from fastapi import APIRouter

from app.api.v1.endpoints import health,chat

router = APIRouter()

router.include_router(
    health.router,
    tags=["Health"],
)
router.include_router(
    chat.router,
    tags=["Chat"],
)