import logging
import psycopg2
import requests
from typing import Optional
from config import settings
from database import supabase

logger = logging.getLogger(__name__)

_conn = None

def _get_connection():
    """Ленивое подключение к Railway PostgreSQL."""
    global _conn
    if _conn is None or _conn.closed:
        try:
            _conn = psycopg2.connect(settings.RAILWAY_DATABASE_URL)
            _conn.autocommit = True
            logger.info("Подключено к Railway PostgreSQL (Photos)")
            
            # На случай если таблица еще не создана ботом
            with _conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS employee_photos (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT UNIQUE NOT NULL,
                        photo_data BYTEA NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                """)
        except Exception as e:
            logger.error("Ошибка подключения к Railway PostgreSQL: %s", e)
            raise e
    return _conn


def save_photo_bytes(telegram_id: int, photo_bytes: bytes):
    """Сохраняет скачанное фото в БД."""
    try:
        conn = _get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO employee_photos (telegram_id, photo_data, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (telegram_id) DO UPDATE SET photo_data = EXCLUDED.photo_data, updated_at = NOW()
                """,
                (telegram_id, psycopg2.Binary(photo_bytes))
            )
    except Exception as e:
        logger.error(f"Ошибка сохранения фото в Railway PG для {telegram_id}: {e}")


def _download_telegram_photo(telegram_id: int) -> Optional[bytes]:
    """Фолбэк: скачивает фото напрямую из Telegram API, если его нет в Railway."""
    try:
        if not settings.BOT_TOKEN:
            return None
            
        # 1. Получаем photo_file_id из Supabase
        res = supabase.table("employees").select("photo_file_id").eq("telegram_id", telegram_id).execute()
        if not res.data or not res.data[0].get("photo_file_id"):
            return None
            
        file_id = res.data[0]["photo_file_id"]
        
        # 2. Обращаемся к API Telegram за file_path
        r_file = requests.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getFile?file_id={file_id}", timeout=10)
        data = r_file.json()
        if not data.get("ok"):
            logger.error(f"Cannot getFile from TG for {telegram_id}: {data}")
            return None
        file_path = data["result"]["file_path"]
        
        # 3. Скачиваем само фото
        r_photo = requests.get(f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path}", timeout=30)
        if r_photo.status_code == 200:
            photo_bytes = r_photo.content
            # Сохраняем в Railway PG на будущее!
            save_photo_bytes(telegram_id, photo_bytes)
            logger.info(f"Успешно мигрировано фото {telegram_id} из Telegram в Railway PG (размер: {len(photo_bytes)} байт)")
            return photo_bytes
    except Exception as e:
        logger.error(f"Фолбэк ошибка при скачивании из TG для {telegram_id}: {e}")
    return None


def get_photo_bytes(telegram_id: int) -> Optional[bytes]:
    """Получает байты фотографии из базы данных по telegram_id."""
    try:
        conn = _get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT photo_data FROM employee_photos WHERE telegram_id = %s",
                (telegram_id,)
            )
            row = cur.fetchone()
            if row and row[0]:
                return bytes(row[0])
    except Exception as e:
        logger.error("Ошибка при получении фото для telegram_id=%s из Railway: %s", telegram_id, e)
        # Сброс соединения при ошибке
        global _conn
        if _conn:
            try:
                _conn.close()
            except:
                pass
            _conn = None

    # Если фото не найдено в БД, попробуем скачать его из Telegram (миграция на лету)
    return _download_telegram_photo(telegram_id)
