from pydantic import BaseModel, Field

from app.common.schemas import EntityModel, Latitude, Longitude
from app.features.city.enums import CitySortBy
from app.features.trip.enums import SortOrder


class CityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    longitude: Longitude
    latitude: Latitude


class CityCreate(CityBase):
    pass


class CityUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    longitude: Longitude | None = None
    latitude: Latitude | None = None


class CityRead(CityBase, EntityModel):
    pass


class CityQueryParams(BaseModel):
    """Query parameters for filtering and sorting cities."""

    search: str | None = Field(None, description='Search cities by name')

    limit: int = Field(20, ge=1, le=100, description='Number of items per page')
    offset: int = Field(0, ge=0, description='Number of items to skip')

    sort_by: CitySortBy = Field(CitySortBy.NAME, description='Sort by field')
    sort_order: SortOrder = Field(SortOrder.ASC, description='Sort order')


class CityListResponse(BaseModel):
    """Response model for paginated cities list."""

    items: list[CityRead]
    total: int
    limit: int
    offset: int
