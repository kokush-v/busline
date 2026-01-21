from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.core.logging_config import setup_logging
from app.middlewares.logging_middleware import LoggingMiddleware
from app.features.city.route import router as city_router
import structlog

setup_logging()

logger = structlog.get_logger()


def get_application() -> FastAPI:
    application = FastAPI(
        title="Busline API",
        version="1.0.0",
        description="API for Busline application",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_middleware(LoggingMiddleware)

    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception on {request.method} {request.url.path}", exc=exc
        )
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error", "detail": str(exc)},
        )

    application.include_router(city_router)

    return application


app = get_application()


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
