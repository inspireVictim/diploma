from collections.abc import Sequence

from app.application.interfaces import BookingRepository, FeedbackRepository, ServiceRepository
from app.application.schemas import BookingCreate, BookingRead, FeedbackCreate, FeedbackRead, ServiceRead
from app.domain.exceptions import EntityNotFoundError


class CatalogService:
    def __init__(self, services: ServiceRepository) -> None:
        self._services = services

    def list_services(self) -> Sequence[ServiceRead]:
        return self._services.list_services()


class BookingService:
    def __init__(self, bookings: BookingRepository, services: ServiceRepository) -> None:
        self._bookings = bookings
        self._services = services

    def create_booking(self, payload: BookingCreate) -> BookingRead:
        if not self._services.exists(payload.service_id):
            raise EntityNotFoundError("Service", payload.service_id)
        return self._bookings.create(payload)

    def list_bookings(self) -> Sequence[BookingRead]:
        return self._bookings.list_all()

    def delete_booking(self, booking_id: int) -> None:
        if not self._bookings.delete(booking_id):
            raise EntityNotFoundError("Booking", booking_id)


class FeedbackService:
    def __init__(self, feedbacks: FeedbackRepository) -> None:
        self._feedbacks = feedbacks

    def create_feedback(self, payload: FeedbackCreate) -> FeedbackRead:
        return self._feedbacks.create(payload)
