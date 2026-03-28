from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import supabase

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Проверяет JWT токен и возвращает данные пользователя."""
    token = credentials.credentials

    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            raise HTTPException(status_code=401, detail="Невалидный токен")

        return {"id": user.id, "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Ошибка авторизации: {str(e)}")
