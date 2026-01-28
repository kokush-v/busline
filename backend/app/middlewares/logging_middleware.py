from pathlib import Path
import time
import traceback
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.settings.env import get_env_settings

logger = structlog.get_logger()

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        await logger.ainfo(
            'http_request_start',
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            # Handle ASGI-level exceptions
            process_time = time.perf_counter() - start_time

            await logger.aerror(
                'asgi_exception',
                error_type=type(exc).__name__,
                error_message=str(exc),
                duration=f'{process_time:.4f}s',
            )

            # Write to file in dev mode
            settings = get_env_settings()
            if settings.ENVIRONMENT == 'dev':
                log_file = Path('logs/error.log')
                with log_file.open('a') as f:
                    f.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] {type(exc).__name__}\n')
                    f.write(f'Path: {request.url.path} | Method: {request.method}\n')
                    f.write(f'Error: {str(exc)}\n')
                    f.write('Stacktrace:\n')
                    f.write(traceback.format_exc())
                    f.write('\n' + '=' * 80 + '\n\n')

            return JSONResponse(
                status_code=500,
                content={
                    'error': {
                        'message': 'An unexpected error occurred',
                        'code': type(exc).__name__,
                    }
                },
            )

        process_time = time.perf_counter() - start_time

        response.headers['X-Request-ID'] = request_id

        await logger.ainfo(
            'http_request_end',
            status_code=response.status_code,
            duration=f'{process_time:.4f}s',
        )
        return response
