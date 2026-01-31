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
    from app.features.bus.models import Bus
    from app.features.seat.models import Seat
    from app.features.trip_stop.models import TripStop


class Trip(Base):
    """Represents a trip with a bus, route, and available seats."""

    __tablename__ = 'trips'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )

    bus_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('buses.id'),
        nullable=False,
    )
    bus: Mapped['Bus'] = relationship('Bus', lazy='selectin')

    seats_left: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    trip_stops: Mapped[list['TripStop']] = relationship(
        'TripStop',
        back_populates='trip',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    seats: Mapped[list['Seat']] = relationship(
        'Seat',
        back_populates='trip',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    __table_args__ = (CheckConstraint('seats_left >= 0', name='check_seats_left_non_negative'),)
