from fastapi import APIRouter
import logging

from app.core.request_context import request_id_context
from app.dependencies import DatabaseDep, SessionDep
from sqlalchemy import text

from app.auth.dependencies import AuthenticatedPrincipal,principalDep
from app.dependencies import UserServiceDep


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

@router.get("/health/db")
async def health_check_db(SessionDep: SessionDep) -> dict[str, str]:
    try:
        # Perform a simple query to check database connectivity
        SessionDep.execute(text("SELECT 1"))
        logger.info("Database health check passed")
        return {
            "status": "healthy",
            "request_id": request_id_context.get(),
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "request_id": request_id_context.get()
        }



@router.get("/health/me")
async def get_me(
    principalDep: principalDep,
    UserServiceDep: UserServiceDep
    )-> dict[str, str]:
        print(principalDep.cognito_sub)
        user = UserServiceDep.get_or_create_user(principalDep.cognito_sub)
        
        return {
           "user_id": str(user.id),
            "cognito_sub": principalDep.cognito_sub,
        }   