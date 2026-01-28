import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import structlog

from app.core.exeptions import setup_exceptions_handler
from app.features.bus.route import router as bus_router
from app.features.city.route import router as city_router
from app.middlewares.logging_middleware import LoggingMiddleware

logger = structlog.get_logger()
logging_logger = logging.getLogger('api')


def get_application() -> FastAPI:
    application = FastAPI(
        title='Busline API',
        version='1.0.0',
        description='API for Busline application',
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    application.add_middleware(LoggingMiddleware)

    application.include_router(bus_router)
    application.include_router(city_router)

    return application


app = get_application()

setup_exceptions_handler(app)


@app.get('/health', tags=['Health'])
async def health_check():
    return {'status': 'healthy', 'version': '1.0.0'}
