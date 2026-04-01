import logging
import psycopg2
from config import settings

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
        except Exception as e:
            logger.error("Ошибка подключения к Railway PostgreSQL: %s", e)
            raise e
    return _conn

def get_photo_bytes(telegram_id: int) -> bytes | None:
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
        logger.error("Ошибка при получении фото для telegram_id=%s: %s", telegram_id, e)
        # Сброс соединения при ошибке, чтобы переподключиться при следующем запросе
        global _conn
        if _conn:
            try:
                _conn.close()
            except:
                pass
            _conn = None

    return None
