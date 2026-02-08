from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.features.ticket.enums import PdfStatus

if TYPE_CHECKING:
    from app.features.order.models import Order
    from app.features.stop.models import Stop
    from app.features.trip.models import Trip


class Ticket(Base):
    """Represents a ticket for a passenger in an order."""

    __tablename__ = 'tickets'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('orders.id', ondelete='CASCADE'),
        nullable=False,
    )

    seat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('seats.id'),
        unique=True,
        nullable=False,
    )

    # Passenger Data
    passenger_name: Mapped[str] = mapped_column(String(100), nullable=False)
    passenger_email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    passenger_age: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Route & Meta
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('trips.id'),
        nullable=False,
    )

    start_stop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('stops.id'),
        nullable=False,
    )

    finish_stop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('stops.id'),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # PDF Generation
    pdf_status: Mapped[PdfStatus] = mapped_column(
        Enum(PdfStatus, name='pdfstatus'),
        default=PdfStatus.PENDING,
        server_default=PdfStatus.PENDING.value,
        nullable=False,
    )
    pdf_s3_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pdf_error: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Notification
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false', nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index(
            'ix_tickets_pending_notification',
            'trip_id',
            'start_stop_id',
            postgresql_where=text('is_notified = false'),
        ),
    )

    order: Mapped['Order'] = relationship('Order', back_populates='tickets')
    trip: Mapped['Trip'] = relationship('Trip', foreign_keys=[trip_id])
    start_stop: Mapped['Stop'] = relationship('Stop', foreign_keys=[start_stop_id])
    finish_stop: Mapped['Stop'] = relationship('Stop', foreign_keys=[finish_stop_id])
