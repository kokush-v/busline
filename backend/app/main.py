import logging

from fastapi import FastAPI
import structlog

from app.core.exeptions import setup_exceptions_handler
from app.features.auth.route import router as auth_router
from app.features.bus.route import router as bus_router
from app.features.city.route import router as city_router
from app.features.order.route import router as order_router
from app.features.payment.route import router as payment_router
from app.features.seat.route import router as seat_router
from app.features.stop.route import router as stop_router
from app.features.ticket.route import router as ticket_router
from app.features.trip.route import router as trip_router
from app.features.user.route import router as user_router
from app.middlewares.logging_middleware import LoggingMiddleware

logger = structlog.get_logger()
logging_logger = logging.getLogger('api')


def get_application(include_middlewares: bool = True) -> FastAPI:
    application = FastAPI(
        title='Busline API',
        version='1.0.0',
        description='API for Busline application',
    )

    setup_exceptions_handler(application)

    if include_middlewares:
        application.add_middleware(LoggingMiddleware)

    application.include_router(auth_router)
    application.include_router(bus_router)
    application.include_router(city_router)
    application.include_router(trip_router)
    application.include_router(stop_router)
    application.include_router(order_router)
    application.include_router(payment_router)
    application.include_router(seat_router)
    application.include_router(ticket_router)
    application.include_router(user_router)

    @application.get('/health', tags=['Health'])
    async def health_check():
        return {'status': 'healthy', 'version': '1.0.0'}

    @application.on_event('startup')
    async def startup_banner():
        base_url = 'http://localhost:8000'
        print(  # noqa: T201
            f'\n'
            f'  \033[1;36mBusLine API v1.0.0\033[0m\n'
            f'\n'
            f'  \033[32mBase URL:\033[0m  {base_url}\n'
            f'  \033[32mDocs:\033[0m      {base_url}/docs\n'
            f'  \033[32mReDoc:\033[0m     {base_url}/redoc\n'
        )

    return application


app = get_application()
