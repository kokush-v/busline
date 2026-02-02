from enum import StrEnum


class UserRole(StrEnum):
    """User role enumeration for RBAC."""

    ADMIN = 'ADMIN'
    USER = 'USER'
