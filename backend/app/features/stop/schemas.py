from uuid import UUID

from pydantic import BaseModel, Field

from app.common.schemas import EntityModel, Latitude, Longitude


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


class StopQueryParams(BaseModel):
    """Query parameters for filtering and paginating stops."""

    search: str | None = Field(None, description='Search stops by city or stop name')

    limit: int = Field(20, ge=1, le=100, description='Number of items per page')
    offset: int = Field(0, ge=0, description='Number of items to skip')


class StopListResponse(BaseModel):
    """Response model for paginated stops list."""

    items: list[StopRead]
    total: int
    limit: int
    offset: int
