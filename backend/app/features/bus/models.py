from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Bus(Base):
    """Represents a bus with its properties and media."""

    __tablename__ = 'buses'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    seats_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    number_plate: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (CheckConstraint('seats_quantity >= 0', name='check_seats_quantity_non_negative'),)
