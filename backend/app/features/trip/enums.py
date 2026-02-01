import enum


class TripSortBy(enum.StrEnum):
    """Sort options for trips."""

    DEPARTURE_TIME = 'DEPARTURE_TIME'
    PRICE = 'PRICE'
    SEATS_LEFT = 'SEATS_LEFT'
    CREATED_AT = 'CREATED_AT'


class SortOrder(enum.StrEnum):
    """Sort order options."""

    ASC = 'ASC'
    DESC = 'DESC'
