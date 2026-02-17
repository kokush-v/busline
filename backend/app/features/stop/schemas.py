from uuid import UUID

from pydantic import BaseModel, Field

from app.common.schemas import EntityModel, Latitude, Longitude, PaginatedResponse, QueryParams


class StopBase(BaseModel):
    city_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    latitude: Latitude
    longitude: Longitude


class StopCreate(StopBase):
    pass


class StopUpdate(BaseModel):
    city_id: UUID | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    latitude: Latitude | None = None
    longitude: Longitude | None = None


class StopRead(StopBase, EntityModel):
    pass


class StopQueryParams(QueryParams):
    """Query parameters for filtering and paginating stops."""

    pass


class StopListResponse(PaginatedResponse[StopRead]):
    """Response model for paginated stops list."""

    pass


class StopSearchParams(BaseModel):
    search: str = ''
    limit: int = Field(10, ge=1, le=100)
    cursor: UUID | None = None


class StopSearchItem(BaseModel):
    id: UUID
    name: str
    city_name: str


class StopSearchResponse(BaseModel):
    items: list[StopSearchItem]
    next_cursor: UUID | None = None
    has_more: bool = False
