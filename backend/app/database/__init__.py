"""Centralized SQLAlchemy model imports for Alembic autogenerate."""

from app.database.db import Base
from app.features.city.models import City

__all__ = ["Base", "City"]
