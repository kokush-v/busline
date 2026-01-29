from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.common.schemas import EntityModel
from app.features.trip_stop.schemas import TripStopRead


class TripBase(BaseModel):
    bus_id: UUID


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    bus_id: UUID | None = None


class TripRead(EntityModel):
    bus_id: UUID
    seats_left: int
    trip_stops: list[TripStopRead]


class TripReadPublic(BaseModel):
    """Public view of trip with limited information."""

    id: UUID
    bus_id: UUID
    seats_left: int
    trip_stops: list[TripStopRead]
    created_at: datetime
