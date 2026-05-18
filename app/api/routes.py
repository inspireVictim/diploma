from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_booking_service,
    get_catalog_service,
    get_feedback_service,
    require_admin,
)
from app.application.schemas import BookingCreate, BookingRead, FeedbackCreate, FeedbackRead, ServiceRead
from app.application.services import BookingService, CatalogService, FeedbackService
from app.domain.exceptions import EntityNotFoundError


public_router = APIRouter(prefix="/api", tags=["public"])
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@public_router.get("/services", response_model=list[ServiceRead])
def list_services(catalog: CatalogService = Depends(get_catalog_service)) -> Sequence[ServiceRead]:
    return catalog.list_services()


@public_router.post("/bookings", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    bookings: BookingService = Depends(get_booking_service),
) -> BookingRead:
    try:
        return bookings.create_booking(payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@public_router.post("/feedbacks", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreate,
    feedbacks: FeedbackService = Depends(get_feedback_service),
) -> FeedbackRead:
    return feedbacks.create_feedback(payload)


@admin_router.get("/bookings", response_model=list[BookingRead])
def list_bookings(bookings: BookingService = Depends(get_booking_service)) -> Sequence[BookingRead]:
    return bookings.list_bookings()


@admin_router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: int,
    bookings: BookingService = Depends(get_booking_service),
) -> None:
    try:
        bookings.delete_booking(booking_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
