from enum import StrEnum


class TripSortBy(StrEnum):
    DEPARTURE_TIME = 'DEPARTURE_TIME'
    PRICE = 'PRICE'
    SEATS_LEFT = 'SEATS_LEFT'
    CREATED_AT = 'CREATED_AT'


class SortOrder(StrEnum):
    ASC = 'ASC'
    DESC = 'DESC'
