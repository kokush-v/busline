from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator

from app.common.schemas import EntityModel
from app.features.trip_stop.schemas import TripStopCreate, TripStopRead


class TripBase(BaseModel):
    bus_id: UUID


class TripCreate(TripBase):
    stops: list[TripStopCreate] = []

    @model_validator(mode='after')
    def validate_stops_count(self) -> 'TripCreate':
        if len(self.stops) < 2:
            raise ValueError('Trip must have at least 2 stops')
        return self

    model_config = {
        'json_schema_extra': {
            'example': {
                'bus_id': '550e8400-e29b-41d4-a716-446655440000',
                'stops': [
                    {
                        'stop_id': '550e8400-e29b-41d4-a716-446655440001',
                        'position_index': 1,
                        'arrival_time': '2026-01-28T08:00:00',
                        'departure_time': '2026-01-28T08:15:00',
                    },
                    {
                        'stop_id': '550e8400-e29b-41d4-a716-446655440002',
                        'position_index': 2,
                        'arrival_time': '2026-01-28T09:00:00',
                        'departure_time': '2026-01-28T09:15:00',
                    },
                ],
            }
        }
    }


class TripUpdate(BaseModel):
    stops: list[TripStopCreate] | None = None

    @model_validator(mode='after')
    def validate_stops_logic(self) -> 'TripUpdate':
        if not self.stops:
            return self

        indices = [s.position_index for s in self.stops]
        if len(indices) != len(set(indices)):
            raise ValueError('Each stop must have a unique position_index')

        sorted_stops = sorted(self.stops, key=lambda x: x.position_index)

        for i in range(len(sorted_stops) - 1):
            current_stop = sorted_stops[i]
            next_stop = sorted_stops[i + 1]

            if next_stop.arrival_time <= current_stop.departure_time:
                raise ValueError(
                    f'Stop at index {next_stop.position_index} arrival time must be '
                    f'after stop at index {current_stop.position_index} departure time'
                )

        return self


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
