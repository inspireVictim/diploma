from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "service.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            vehicle TEXT NOT NULL,
            service_date TEXT NOT NULL,
            service_type TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

class Booking(BaseModel):
    client_name: str
    vehicle: str
    service_date: str
    service_type: str

@app.post("/booking")
async def create_booking(booking: Booking):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO maintenance_requests (client_name, vehicle, service_date, service_type) VALUES (?, ?, ?, ?)",
                   (booking.client_name, booking.vehicle, booking.service_date, booking.service_type))
    conn.commit()
    conn.close()
    return {"status": "ok"}

# API ДЛЯ АДМИНКИ
@app.get("/admin/requests")
async def get_requests():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maintenance_requests ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()
    return data

@app.delete("/admin/requests/{req_id}")
async def delete_request(req_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM maintenance_requests WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)