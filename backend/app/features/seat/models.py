from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.features.seat.enums import SeatStatus
from app.database.db import Base

if TYPE_CHECKING:
    from app.features.trip.models import Trip


class Seat(Base):
    """Represents a specific seat in a trip."""

    __tablename__ = 'seats'

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

    position_index: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[SeatStatus] = mapped_column(
        Enum(SeatStatus, name='seatstatus'),
        default=SeatStatus.FREE,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    trip: Mapped['Trip'] = relationship('Trip', back_populates='seats')
