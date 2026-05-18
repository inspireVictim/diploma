from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from app.application.schemas import BookingCreate, BookingRead, FeedbackCreate, FeedbackRead, ServiceRead
from app.infrastructure.database import get_connection


class SQLiteServiceRepository:
    def list_services(self) -> Sequence[ServiceRead]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, category_id, title, description, price
                FROM Services
                ORDER BY category_id, id
                """
            ).fetchall()
        return [
            ServiceRead(
                id=row["id"],
                category_id=row["category_id"],
                title=row["title"],
                description=row["description"],
                price=Decimal(str(row["price"])),
            )
            for row in rows
        ]

    def exists(self, service_id: int) -> bool:
        with get_connection() as conn:
            row = conn.execute("SELECT 1 FROM Services WHERE id = ?", (service_id,)).fetchone()
        return row is not None


class SQLiteBookingRepository:
    def create(self, payload: BookingCreate) -> BookingRead:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO Bookings (client_name, device, service_id, service_date)
                VALUES (?, ?, ?, ?)
                """,
                (
                    payload.client_name,
                    payload.device,
                    payload.service_id,
                    payload.service_date.isoformat(),
                ),
            )
            row = conn.execute(
                """
                SELECT id, client_name, device, service_id, service_date, status, created_at
                FROM Bookings
                WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return _booking_from_row(row)

    def list_all(self) -> Sequence[BookingRead]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, client_name, device, service_id, service_date, status, created_at
                FROM Bookings
                ORDER BY id DESC
                """
            ).fetchall()
        return [_booking_from_row(row) for row in rows]

    def delete(self, booking_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM Bookings WHERE id = ?", (booking_id,))
            return cursor.rowcount > 0


class SQLiteFeedbackRepository:
    def create(self, payload: FeedbackCreate) -> FeedbackRead:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO Feedbacks (name, email_or_phone, message)
                VALUES (?, ?, ?)
                """,
                (payload.name, payload.email_or_phone, payload.message),
            )
            row = conn.execute(
                """
                SELECT id, name, email_or_phone, message, created_at
                FROM Feedbacks
                WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return FeedbackRead(
            id=row["id"],
            name=row["name"],
            email_or_phone=row["email_or_phone"],
            message=row["message"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


def _booking_from_row(row) -> BookingRead:
    return BookingRead(
        id=row["id"],
        client_name=row["client_name"],
        device=row["device"],
        service_id=row["service_id"],
        service_date=datetime.fromisoformat(row["service_date"]),
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )
