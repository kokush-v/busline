from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    PAID = 'PAID'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'
