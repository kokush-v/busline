import enum


class OrderStatus(enum.StrEnum):
    """Represents the status of a reservation order."""

    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    PAID = 'PAID'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'
