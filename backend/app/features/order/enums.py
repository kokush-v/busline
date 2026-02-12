from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    PAID = 'PAID'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


class ProfileOrderFilterEnum(StrEnum):
    """Filter enum for user profile orders.

    Groups order statuses into logical categories:
    - ALL: All orders
    - COMPLETED: Successfully paid orders (PAID)
    - PENDING: Orders in progress (PROCESSING, PENDING)
    - CANCELLED: Failed or cancelled orders (FAILED, CANCELLED)
    """

    ALL = 'ALL'
    COMPLETED = 'COMPLETED'
    PENDING = 'PENDING'
    CANCELLED = 'CANCELLED'

    def get_statuses(self) -> list[OrderStatus] | None:
        """Get the list of OrderStatus values for this filter."""
        mapping = {
            ProfileOrderFilterEnum.ALL: None,  # No filter, return all
            ProfileOrderFilterEnum.COMPLETED: [OrderStatus.PAID],
            ProfileOrderFilterEnum.PENDING: [OrderStatus.PROCESSING, OrderStatus.PENDING],
            ProfileOrderFilterEnum.CANCELLED: [OrderStatus.FAILED, OrderStatus.CANCELLED],
        }
        return mapping[self]
