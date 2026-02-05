from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.common.schemas import EntityModel, PaginatedResponse, QueryParams
from app.features.trip.enums import TripSortBy
from app.features.trip_stop.schemas import TripStopCreate, TripStopRead


class TripBase(BaseModel):
    bus_id: UUID
    price_per_seat: float


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
                'price_per_seat': 150.00,
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
    price_per_seat: float | None = None
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
    price_per_seat: float
    seats_left: int
    trip_stops: list[TripStopRead]


class TripReadPublic(BaseModel):
    """Public view of trip with limited information."""

    id: UUID
    bus_id: UUID
    price_per_seat: float
    seats_left: int
    trip_stops: list[TripStopRead]
    created_at: datetime


class TripQueryParams(QueryParams):
    """Query parameters for filtering and sorting trips."""

    sort_by: TripSortBy = Field(TripSortBy.DEPARTURE_TIME, description='Sort by field')
    from_stop_id: UUID | None = Field(None, description='Filter by departure stop')
    to_stop_id: UUID | None = Field(None, description='Filter by arrival stop')
    departure_date_from: datetime | None = Field(None, description='Filter by minimum departure date')
    departure_date_to: datetime | None = Field(None, description='Filter by maximum departure date')
    min_price: float | None = Field(None, ge=0, description='Filter by minimum price per seat')
    max_price: float | None = Field(None, ge=0, description='Filter by maximum price per seat')
    available_seats_min: int | None = Field(None, ge=0, description='Filter by minimum available seats')


class TripListResponse(PaginatedResponse[TripReadPublic]):
    """Response model for paginated trips list."""

    pass
