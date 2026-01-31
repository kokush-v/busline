import enum


class SeatStatus(enum.StrEnum):
    """Represents the status of a seat in a trip."""

    FREE = 'FREE'
    LOCKED = 'LOCKED'
    SOLD = 'SOLD'
