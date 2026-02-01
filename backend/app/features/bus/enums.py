import enum


class BusSortBy(enum.StrEnum):
    """Sort options for buses."""

    NUMBER_PLATE = 'NUMBER_PLATE'
    COLOR = 'COLOR'
    SEATS_QUANTITY = 'SEATS_QUANTITY'
    CREATED_AT = 'CREATED_AT'
