from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.common.schemas import EntityModel


class TripStopBase(BaseModel):
    stop_id: UUID
    position_index: int
    arrival_time: datetime
    departure_time: datetime

    @field_validator('position_index')
    @classmethod
    def validate_position(cls, v):
        """Validate that position is positive."""
        if v < 1:
            raise ValueError('Position must be greater than or equal to 1')
        return v

    @field_validator('departure_time')
    @classmethod
    def validate_departure_after_arrival(cls, v, info):
        """Validate that departure time is after arrival time."""
        if 'arrival_time' in info.data and v <= info.data['arrival_time']:
            raise ValueError('Departure time must be after arrival time')
        return v


class TripStopCreate(TripStopBase):
    pass


class TripStopUpdate(BaseModel):
    trip_id: UUID | None = None
    stop_id: UUID | None = None
    position_index: int | None = None
    arrival_time: datetime | None = None
    departure_time: datetime | None = None

    @field_validator('position_index')
    @classmethod
    def validate_position(cls, v):
        """Validate that position is positive."""
        if v is not None and v < 1:
            raise ValueError('Position must be greater than or equal to 1')
        return v

    @field_validator('departure_time')
    @classmethod
    def validate_departure_after_arrival(cls, v, info):
        """Validate that departure time is after arrival time."""
        if v is not None and 'arrival_time' in info.data and info.data['arrival_time'] is not None:
            if v <= info.data['arrival_time']:
                raise ValueError('Departure time must be after arrival time')
        return v


class TripStopRead(EntityModel):
    trip_id: UUID
    stop_id: UUID
    position_index: int
    arrival_time: datetime
    departure_time: datetime
