from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


class BusRead(BusBase):
    id: UUID
    photo_url: str | None = None
    thumbnail_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PresignedUrlRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
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
