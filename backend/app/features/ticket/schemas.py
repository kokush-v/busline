from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.common.schemas import EntityModel


class TicketBase(BaseModel):
    passenger_name: str = Field(..., min_length=1, max_length=100)
    passenger_email: str | None = Field(None, max_length=100)
    passenger_age: int | None = Field(None, ge=0, le=150)


class TicketCreate(TicketBase):
    order_id: UUID
    seat_id: UUID
    trip_id: UUID
    start_stop_id: UUID
    finish_stop_id: UUID
    price: Decimal = Field(..., decimal_places=2, ge=0)


class TicketRead(EntityModel):
    order_id: UUID
    seat_id: UUID
    passenger_name: str
    passenger_email: str | None = None
    passenger_age: int | None = None
    trip_id: UUID
    start_stop_id: UUID
    finish_stop_id: UUID
    price: Decimal
    pdf_url: str | None = None


class TicketUpdate(BaseModel):
    passenger_name: str | None = Field(None, min_length=1, max_length=100)
    passenger_email: str | None = Field(None, max_length=100)
    passenger_age: int | None = Field(None, ge=0, le=150)
    pdf_url: str | None = None


class ReserveTicketRequest(BaseModel):
    """Request to reserve a seat."""

    seat_id: UUID
    passenger_name: str = Field(..., min_length=1, max_length=100)
    passenger_email: str | None = Field(None, max_length=100)
    passenger_age: int | None = Field(None, ge=0, le=150)
    start_stop_id: UUID
    finish_stop_id: UUID
    price: Decimal = Field(..., decimal_places=2, ge=0)
