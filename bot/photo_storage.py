"""
Хранилище фотографий сотрудников в Railway PostgreSQL.
Фото хранятся в таблице employee_photos как bytea (бинарные данные).
Связь с таблицей employees (Supabase) через telegram_id.
"""

import logging

import psycopg2
from config import settings

logger = logging.getLogger(__name__)

_conn = None


def _get_connection():
    """Ленивое подключение к Railway PostgreSQL с автопереподключением."""
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(settings.RAILWAY_DATABASE_URL)
        _conn.autocommit = True
        logger.info("✅ Подключение к Railway PostgreSQL установлено")
    return _conn


def ensure_photos_table():
    """Создаёт таблицу employee_photos, если она не существует."""
    conn = _get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employee_photos (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                photo_data BYTEA NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_employee_photos_telegram_id
                ON employee_photos (telegram_id);
        """)
    logger.info("✅ Таблица employee_photos готова")


def save_photo(telegram_id: int, photo_bytes: bytes) -> None:
    """Сохраняет или обновляет фото сотрудника."""
    conn = _get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO employee_photos (telegram_id, photo_data, updated_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (telegram_id)
            DO UPDATE SET photo_data = EXCLUDED.photo_data, updated_at = NOW()
            """,
            (telegram_id, psycopg2.Binary(photo_bytes)),
        )
    logger.info("📸 Фото сохранено для telegram_id=%s (%d байт)", telegram_id, len(photo_bytes))


def delete_photo(telegram_id: int) -> None:
    """Удаляет фото сотрудника."""
    conn = _get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM employee_photos WHERE telegram_id = %s",
            (telegram_id,),
        )
    logger.info("🗑 Фото удалено для telegram_id=%s", telegram_id)
