from enum import StrEnum


class UserRoleGroups(StrEnum):
    """User role enumeration for RBAC."""

    ADMIN = 'ADMIN'
    USER = 'USER'


class UserSortBy(StrEnum):
    """User sorting options."""

    EMAIL = 'email'
    NAME = 'name'
    CREATED_AT = 'created_at'
