from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "service.db"


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) >= 2),
    slug TEXT NOT NULL UNIQUE CHECK (length(trim(slug)) >= 2)
);

CREATE TABLE IF NOT EXISTS Services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL CHECK (length(trim(title)) >= 2),
    description TEXT NOT NULL CHECK (length(trim(description)) >= 5),
    price NUMERIC NOT NULL CHECK (price >= 0),
    FOREIGN KEY (category_id)
        REFERENCES Categories(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Portfolio_Projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) >= 2),
    description TEXT NOT NULL CHECK (length(trim(description)) >= 5),
    client_name TEXT NOT NULL CHECK (length(trim(client_name)) >= 2),
    completion_date TEXT NOT NULL CHECK (date(completion_date) IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS Project_Services (
    project_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    PRIMARY KEY (project_id, service_id),
    FOREIGN KEY (project_id)
        REFERENCES Portfolio_Projects(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (service_id)
        REFERENCES Services(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL CHECK (length(trim(client_name)) >= 2),
    device TEXT NOT NULL CHECK (length(trim(device)) >= 2),
    service_id INTEGER NOT NULL,
    service_date TEXT NOT NULL CHECK (datetime(service_date) IS NOT NULL),
    status TEXT NOT NULL DEFAULT 'new'
        CHECK (status IN ('new', 'confirmed', 'completed', 'cancelled')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id)
        REFERENCES Services(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (length(trim(name)) >= 2),
    email_or_phone TEXT NOT NULL CHECK (length(trim(email_or_phone)) >= 5),
    message TEXT NOT NULL CHECK (length(trim(message)) >= 5),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_services_category_id
    ON Services(category_id);
CREATE INDEX IF NOT EXISTS idx_bookings_service_id
    ON Bookings(service_id);
CREATE INDEX IF NOT EXISTS idx_bookings_service_date
    ON Bookings(service_date);
CREATE INDEX IF NOT EXISTS idx_bookings_status
    ON Bookings(status);
CREATE INDEX IF NOT EXISTS idx_project_services_service_id
    ON Project_Services(service_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_created_at
    ON Feedbacks(created_at);
"""


SEED_SQL = """
INSERT OR IGNORE INTO Categories (id, name, slug) VALUES
    (1, 'Диагностика', 'diagnostics'),
    (2, 'Обслуживание', 'maintenance'),
    (3, 'Периферия и сеть', 'peripherals-network');

INSERT OR IGNORE INTO Services (id, category_id, title, description, price) VALUES
    (1, 1, 'Диагностика ноутбука/ПК', 'Полная проверка аппаратной части, накопителя, памяти, температур и операционной системы.', 15000),
    (2, 2, 'Чистка и замена термопасты', 'Разбор устройства, удаление пыли, обслуживание системы охлаждения и замена термоинтерфейса.', 4500),
    (3, 3, 'Настройка принтера и сети', 'Подключение принтера, установка драйверов, настройка печати и доступа по локальной сети.', 3500);

INSERT OR IGNORE INTO Portfolio_Projects
    (id, title, description, client_name, completion_date)
VALUES
    (1, 'Восстановление игрового ноутбука', 'Диагностика, чистка системы охлаждения и настройка Windows после перегрева.', 'Частный клиент', '2026-04-20'),
    (2, 'Настройка офисной печати', 'Подключение сетевого принтера и настройка печати для рабочих мест офиса.', 'Neo Office', '2026-05-02');

UPDATE Categories SET
    name = CASE id
        WHEN 1 THEN 'Диагностика'
        WHEN 2 THEN 'Обслуживание'
        WHEN 3 THEN 'Периферия и сеть'
    END,
    slug = CASE id
        WHEN 1 THEN 'diagnostics'
        WHEN 2 THEN 'maintenance'
        WHEN 3 THEN 'peripherals-network'
    END
WHERE id IN (1, 2, 3);

UPDATE Services SET
    category_id = CASE id WHEN 1 THEN 1 WHEN 2 THEN 2 WHEN 3 THEN 3 END,
    title = CASE id
        WHEN 1 THEN 'Диагностика ноутбука/ПК'
        WHEN 2 THEN 'Чистка и замена термопасты'
        WHEN 3 THEN 'Настройка принтера и сети'
    END,
    description = CASE id
        WHEN 1 THEN 'Полная проверка аппаратной части, накопителя, памяти, температур и операционной системы.'
        WHEN 2 THEN 'Разбор устройства, удаление пыли, обслуживание системы охлаждения и замена термоинтерфейса.'
        WHEN 3 THEN 'Подключение принтера, установка драйверов, настройка печати и доступа по локальной сети.'
    END,
    price = CASE id WHEN 1 THEN 15000 WHEN 2 THEN 4500 WHEN 3 THEN 3500 END
WHERE id IN (1, 2, 3);

UPDATE Portfolio_Projects SET
    title = CASE id
        WHEN 1 THEN 'Восстановление игрового ноутбука'
        WHEN 2 THEN 'Настройка офисной печати'
    END,
    description = CASE id
        WHEN 1 THEN 'Диагностика, чистка системы охлаждения и настройка Windows после перегрева.'
        WHEN 2 THEN 'Подключение сетевого принтера и настройка печати для рабочих мест офиса.'
    END,
    client_name = CASE id
        WHEN 1 THEN 'Частный клиент'
        WHEN 2 THEN 'Neo Office'
    END
WHERE id IN (1, 2);

INSERT OR IGNORE INTO Project_Services (project_id, service_id) VALUES
    (1, 1),
    (1, 2),
    (2, 3);
"""


def _connect(path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(seed: bool = True) -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)
        _migrate_bookings_device_column(conn)
        if seed:
            conn.executescript(SEED_SQL)


def _migrate_bookings_device_column(conn: sqlite3.Connection) -> None:
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(Bookings)").fetchall()
    }
    if "device" not in columns and "vehicle" in columns:
        conn.execute("ALTER TABLE Bookings RENAME COLUMN vehicle TO device")
