from enum import StrEnum


class UserRoleGroups(StrEnum):
    """User role enumeration for RBAC."""

    ADMIN = 'ADMIN'
    USER = 'USER'
