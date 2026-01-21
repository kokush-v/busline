import time
import uuid
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        await logger.ainfo(
            "http_request_start",
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time

            response.headers["X-Request-ID"] = request_id

            await logger.ainfo(
                "http_request_end",
                status_code=response.status_code,
                duration=f"{process_time:.4f}s",
            )
            return response

        except Exception as e:
            process_time = time.perf_counter() - start_time
            await logger.aexception(
                "http_request_error",
                error=str(e),
                duration=f"{process_time:.4f}s",
            )
            raise
