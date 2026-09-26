import logging
import uuid

from fastapi import Request
from app.core.request_context import request_id_context
import time
logger = logging.getLogger(__name__)


async def request_id_middleware(
    request: Request,
    call_next,):
    request_id = request.headers.get(
        "X-Request-ID"
    )
    if not request_id:
        request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    request.state.request_id = request_id
    token = request_id_context.set(request_id)

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        duration = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
        logger.info(
            "HTTP request completed | "
            "method=%s | "
            "path=%s | "
            "status=%s | "
            "duration_ms=%.2f",
            request.method,
            request.url.path,
            getattr(response, "status_code", 500),
            duration,
        )
        request_id_context.reset(token)