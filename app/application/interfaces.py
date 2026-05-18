from collections.abc import Sequence
from typing import Protocol

from app.application.schemas import BookingCreate, BookingRead, FeedbackCreate, FeedbackRead, ServiceRead


class ServiceRepository(Protocol):
    def list_services(self) -> Sequence[ServiceRead]:
        ...

    def exists(self, service_id: int) -> bool:
        ...


class BookingRepository(Protocol):
    def create(self, payload: BookingCreate) -> BookingRead:
        ...

    def list_all(self) -> Sequence[BookingRead]:
        ...

    def delete(self, booking_id: int) -> bool:
        ...


class FeedbackRepository(Protocol):
    def create(self, payload: FeedbackCreate) -> FeedbackRead:
        ...
