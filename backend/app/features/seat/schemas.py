from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.common.schemas import EntityModel
from app.common.statuses import OrderStatus, SeatStatus
from app.features.ticket.schemas import ReserveTicketRequest, TicketRead


class SeatBase(BaseModel):
    position_index: int = Field(..., ge=1)
    status: SeatStatus


class SeatCreate(BaseModel):
    position_index: int = Field(..., ge=1)


class SeatRead(EntityModel):
    trip_id: UUID
    position_index: int
    status: SeatStatus


class SeatUpdate(BaseModel):
    status: SeatStatus


class ReserveSeatRequest(BaseModel):
    """Request to reserve multiple seats."""

    trip_id: UUID
    tickets: list[ReserveTicketRequest] = Field(..., min_items=1)


class ReserveSeatResponse(EntityModel):
    """Response after reservation."""

    status: OrderStatus
    total_price: Decimal
    expires_at: datetime | None = None
    tickets: list[TicketRead]
