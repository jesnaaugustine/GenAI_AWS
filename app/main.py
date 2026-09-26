from contextlib import asynccontextmanager
from app.core.logging import configure_logging
import logging

from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.clients.OpenAI.factory import make_openai_client
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.v1.schemas.error import ErrorResponse, ErrorDetail
from app.core.middleware import request_id_middleware

from app.core.exceptions import AppException
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("Application starting...")
    app.state.settings = get_settings()
    app.state.openai_client = make_openai_client()
    logger.info("OpenAI client created successfully.")


    yield

    # Shutdown
    app.state.openai_client = None
    logger.info("Application shutting down...")


app = FastAPI(
    title="GenAI Chat API",
    version="0.1.0",
    description="Production-oriented GenAI API using FastAPI and Amazon Bedrock",
    lifespan=lifespan,
)

app.middleware("http")(request_id_middleware)
app.include_router(v1_router,prefix="/api/v1")
@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:

    error_response = ErrorResponse(
        error=ErrorDetail(
            code=exc.code,
            message=exc.message,
        )
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:

    logger.exception(
        "Unhandled application exception"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            }
        },
    )