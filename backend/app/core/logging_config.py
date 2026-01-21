import logging.config
import structlog
from app.settings.env import settings


def setup_logging():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.DEBUG:
        processor_final = structlog.dev.ConsoleRenderer()
    else:
        processor_final = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": processor_final,
                "foreign_pre_chain": shared_processors,
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "structured",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "INFO",
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
            },
        },
    }

    logging.config.dictConfig(logging_config)
