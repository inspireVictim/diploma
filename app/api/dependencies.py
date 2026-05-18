from fastapi import Header, HTTPException, status

from app.application.schemas import AdminAuthResult
from app.application.services import BookingService, CatalogService, FeedbackService
from app.infrastructure.repositories import (
    SQLiteBookingRepository,
    SQLiteFeedbackRepository,
    SQLiteServiceRepository,
)


ADMIN_TOKEN = "neo-sync-admin"


def get_catalog_service() -> CatalogService:
    return CatalogService(SQLiteServiceRepository())


def get_booking_service() -> BookingService:
    service_repository = SQLiteServiceRepository()
    return BookingService(SQLiteBookingRepository(), service_repository)


def get_feedback_service() -> FeedbackService:
    return FeedbackService(SQLiteFeedbackRepository())


def require_admin(x_admin_token: str | None = Header(default=None)) -> AdminAuthResult:
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token",
        )
    return AdminAuthResult(scope="admin")
