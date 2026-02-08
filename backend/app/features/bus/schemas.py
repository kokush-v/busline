from typing import Annotated

from pydantic import BaseModel, Field

from app.common.schemas import EntityModel, PaginatedResponse, QueryParams
from app.features.bus.enums import BusSortBy


class BusBase(BaseModel):
    color: str = Field(..., min_length=1, max_length=50)
    seats_quantity: Annotated[int, Field(ge=0)]
    number_plate: str = Field(..., min_length=1, max_length=20)


class BusCreate(BusBase):
    pass


class BusUpdate(BaseModel):
    color: str | None = Field(None, min_length=1, max_length=50)
    seats_quantity: Annotated[int, Field(ge=0)] | None = None
    number_plate: str | None = Field(None, min_length=1, max_length=20)


class BusRead(BusBase, EntityModel):
    photo_url: str | None = None
    thumbnail_url: str | None = None


class PresignedUrlRequest(BaseModel):
    content_type: str = Field(..., pattern=r'^image/(jpeg|png)$')


class PresignedUrlResponse(BaseModel):
    upload_url: str
    photo_key: str
    fields: dict[str, str] | None = None


class PhotoUploadComplete(BaseModel):
    photo_key: str


# TODO: Remove this test schema in production
class TestUploadRequest(BaseModel):
    upload_url: str
    fields: dict[str, str]


class BusQueryParams(QueryParams):
    """Query parameters for filtering and sorting buses."""

    sort_by: BusSortBy = Field(BusSortBy.CREATED_AT, description='Sort by field')
    min_seats: int | None = Field(None, ge=0, description='Minimum seats quantity')
    max_seats: int | None = Field(None, ge=0, description='Maximum seats quantity')
    has_photo: bool | None = Field(None, description='Filter by photo availability')


class BusListResponse(PaginatedResponse[BusRead]):
    """Response model for paginated buses list."""

    pass
