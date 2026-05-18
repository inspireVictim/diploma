from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum


class BookingStatus(StrEnum):
    NEW = "new"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Category:
    id: int
    name: str
    slug: str


@dataclass(frozen=True, slots=True)
class Service:
    id: int
    category_id: int
    title: str
    description: str
    price: Decimal


@dataclass(frozen=True, slots=True)
class PortfolioProject:
    id: int
    title: str
    description: str
    client_name: str
    completion_date: date


@dataclass(frozen=True, slots=True)
class Booking:
    id: int
    client_name: str
    device: str
    service_id: int
    service_date: datetime
    status: BookingStatus
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Feedback:
    id: int
    name: str
    email_or_phone: str
    message: str
    created_at: datetime
