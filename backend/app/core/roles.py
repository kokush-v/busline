from enum import Enum

from fastapi import Depends, HTTPException, status


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user=Depends(lambda: get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to perform this operation",
            )
        return user


# TODO: Should be replaced with actual user retrieval logic
def get_current_user():
    pass
