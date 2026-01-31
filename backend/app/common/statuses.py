import enum


class OrderStatus(str, enum.Enum):
    """Represents the status of a reservation order."""

    PENDING = 'pending'
    PROCESSING = 'processing'
    PAID = 'paid'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class SeatStatus(str, enum.Enum):
    """Represents the status of a seat in a trip."""

    FREE = 'free'
    LOCKED = 'locked'
    SOLD = 'sold'
