from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base

if TYPE_CHECKING:
    from app.features.stop.models import Stop
    from app.features.trip.models import Trip


class TripStop(Base):
    """Represents a stop in a specific trip with schedule information."""

    __tablename__ = 'trip_stops'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('trips.id', ondelete='CASCADE'),
        nullable=False,
    )
    trip: Mapped['Trip'] = relationship('Trip', back_populates='trip_stops')

    stop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('stops.id', ondelete='CASCADE'),
        nullable=False,
    )
    stop: Mapped['Stop'] = relationship('Stop', back_populates='trip_stops')

    position_index: Mapped[int] = mapped_column(Integer, nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint('departure_time > arrival_time', name='check_departure_after_arrival'),
        CheckConstraint('position_index >= 1', name='check_position_positive'),
    )
