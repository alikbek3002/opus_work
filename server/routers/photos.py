from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from services.photo_service import get_photo_bytes

router = APIRouter(prefix="/api/photos", tags=["Фото"])


@router.get("/{telegram_id}")
async def get_photo(telegram_id: int):
    """
    Возвращает фото сотрудника по его telegram_id.
    Данные берутся из Railway PostgreSQL.
    """
    photo_data = get_photo_bytes(telegram_id)
    
    if not photo_data:
        raise HTTPException(status_code=404, detail="Фото не найдено")
    
    # Указываем браузеру кэшировать недолго (или revalidate),
    # чтобы при удалении/изменении анкеты фото обновлялось, а не висело в кэше браузера.
    headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    
    # Telegram обычно отдает фото как jpeg
    return Response(content=photo_data, media_type="image/jpeg", headers=headers)
