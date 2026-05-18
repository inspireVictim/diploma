from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.entities import BookingStatus


ShortText = Annotated[str, Field(min_length=2, max_length=120)]
LongText = Annotated[str, Field(min_length=5, max_length=2_000)]


class CategoryRead(BaseModel):
    id: int
    name: str
    slug: str


class ServiceCreate(BaseModel):
    category_id: int = Field(gt=0)
    title: ShortText
    description: LongText
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)


class ServiceRead(ServiceCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PortfolioProjectRead(BaseModel):
    id: int
    title: str
    description: str
    client_name: str
    completion_date: date
    service_ids: list[int] = Field(default_factory=list)


class BookingCreate(BaseModel):
    client_name: ShortText
    device: ShortText
    service_id: int = Field(gt=0)
    service_date: datetime

    @field_validator("service_date")
    @classmethod
    def validate_future_service_date(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        if value <= datetime.now(timezone.utc):
            raise ValueError("service_date must be in the future")
        return value


class BookingRead(BaseModel):
    id: int
    client_name: str
    device: str
    service_id: int
    service_date: datetime
    status: BookingStatus
    created_at: datetime


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class FeedbackCreate(BaseModel):
    name: ShortText
    email_or_phone: Annotated[str, Field(min_length=5, max_length=120)]
    message: LongText

    @field_validator("email_or_phone")
    @classmethod
    def validate_contact(cls, value: str) -> str:
        normalized = value.strip()
        has_email_shape = "@" in normalized and "." in normalized.split("@")[-1]
        digits_count = sum(symbol.isdigit() for symbol in normalized)
        if not has_email_shape and digits_count < 7:
            raise ValueError("email_or_phone must contain a valid email or phone number")
        return normalized


class FeedbackRead(BaseModel):
    id: int
    name: str
    email_or_phone: str
    message: str
    created_at: datetime


class AdminAuthResult(BaseModel):
    scope: Literal["admin"]
