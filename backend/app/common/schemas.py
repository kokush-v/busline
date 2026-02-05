from datetime import datetime
from typing import Annotated, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import SortOrder

T = TypeVar('T')


# Geographic coordinates types
Latitude = Annotated[float, Field(ge=-90, le=90, description='Latitude coordinate')]
Longitude = Annotated[float, Field(ge=-180, le=180, description='Longitude coordinate')]


class EntityModel(BaseModel):
    """Base model for entities with common fields."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QueryParams(BaseModel):
    """Base query parameters for pagination and search."""

    search: str | None = Field(None, description='Search query')
    limit: int = Field(10, ge=1, le=100, description='Number of items per page')
    offset: int = Field(0, ge=0, description='Number of items to skip')
    sort_order: SortOrder = Field(SortOrder.ASC, description='Sort order')


class PaginatedResponse[T](BaseModel):
    """Paginated response model."""

    items: list[T]
    total: int
    limit: int
    offset: int
