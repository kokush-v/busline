"""Centralized SQLAlchemy model imports for Alembic autogenerate."""

from app.database.db import Base
from app.features.bus.models import Bus
from app.features.city.models import City
from app.features.stop.models import Stop
from app.features.trip.models import Trip
from app.features.trip_stop.models import TripStop

__all__ = ['Base', 'City', 'Bus', 'Stop', 'Trip', 'TripStop']
