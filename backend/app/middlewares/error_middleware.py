from pathlib import Path
import time
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.settings.env import get_env_settings
from app.utils.error_handler import normalize_error

logger = structlog.get_logger()

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)


class ErrorMiddleware(BaseHTTPMiddleware):
    """
    Middleware для перехоплення та обробки помилок.
    Перетворює исключения на JSON відповіді з відповідними HTTP статус-кодами.
    """

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except Exception as exc:
            # Отримуємо нормалізовану помилку (статус-код та повідомлення)
            status_code, error_message = normalize_error(exc)

            # Логуємо помилку
            await logger.aerror(
                'unhandled_exception',
                path=request.url.path,
                method=request.method,
                error_message=str(exc),
                error_type=type(exc).__name__,
                exc_info=True,
            )

            # Записуємо помилку у файл в режимі dev
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

            # Повертаємо JSON відповідь з помилкою
            return JSONResponse(
                status_code=status_code,
                content={
                    'detail': error_message,
                    'error_type': type(exc).__name__,
                },
            )
