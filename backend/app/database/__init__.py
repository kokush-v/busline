"""Centralized SQLAlchemy model imports for Alembic autogenerate."""

from app.database.db import Base
from app.features.bus.models import Bus
from app.features.city.models import City
from app.features.order.models import Order
from app.features.seat.models import Seat
from app.features.stop.models import Stop
from app.features.ticket.models import Ticket
from app.features.trip.models import Trip
from app.features.trip_stop.models import TripStop

__all__ = ['Base', 'City', 'Bus', 'Stop', 'Trip', 'TripStop', 'Order', 'Seat', 'Ticket']
