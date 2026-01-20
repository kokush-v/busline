import logging
from typing import Optional

from app.config.logging_config import setup_logging


class LoggerService:
    """Centralized logging service for the application."""

    _initialized = False

    def __init__(self, name: str):
        # Setup logging only once on first instantiation
        if not LoggerService._initialized:
            setup_logging()
            LoggerService._initialized = True

        self.logger = logging.getLogger(name)

    def info(self, message: str) -> None:
        """Log info level message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning level message."""
        self.logger.warning(message)

    def error(self, message: str, exc: Optional[Exception] = None) -> None:
        """Log error level message with optional exception info."""
        self.logger.error(message, exc_info=exc)

    def debug(self, message: str) -> None:
        """Log debug level message."""
        self.logger.debug(message)

    def critical(self, message: str, exc: Optional[Exception] = None) -> None:
        """Log critical level message with optional exception info."""
        self.logger.critical(message, exc_info=exc)
