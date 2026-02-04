from enum import StrEnum


class TripSortBy(StrEnum):
    DEPARTURE_TIME = 'departure_time'
    PRICE = 'price'
    SEATS_LEFT = 'seats_left'
    CREATED_AT = 'created_at'
