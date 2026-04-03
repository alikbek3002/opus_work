from fastapi import APIRouter, HTTPException
from database import supabase, supabase_anon
from config import settings
from models.schemas import RegisterRequest, LoginRequest, PasswordResetRequest, AuthResponse

router = APIRouter(prefix="/api/auth", tags=["Авторизация"])


@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest):
    """Регистрация нового работодателя."""
    try:
        # Создаём пользователя в Supabase Auth
        auth_response = supabase_anon.auth.sign_up({
            "email": data.email,
            "password": data.password,
        })

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Ошибка при регистрации")

        user_id = auth_response.user.id

        # Создаём или обновляем запись в таблице employers
        supabase.table("employers").upsert({
            "id": user_id,
            "full_name": data.full_name,
            "email": data.email,
            "company_name": data.company_name,
        }).execute()

        if not auth_response.session:
            raise HTTPException(
                status_code=400,
                detail="Подтверждение email включено в Supabase. Пожалуйста, отключите 'Confirm email' в настройках Authentication -> Providers -> Email."
            )

        return AuthResponse(
            access_token=auth_response.session.access_token,
            user_id=user_id,
            email=data.email,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest):
    """Авторизация работодателя."""
    try:
        auth_response = supabase_anon.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })

        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Неверный email или пароль")

        return AuthResponse(
            access_token=auth_response.session.access_token,
            user_id=auth_response.user.id,
            email=data.email,
        )

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Ошибка авторизации: {str(e)}")


@router.post("/reset-password")
async def reset_password(data: PasswordResetRequest):
    """Отправить письмо для сброса пароля работодателю."""
    try:
        redirect_to = f"{settings.APP_URL.rstrip('/')}/reset-password"
        supabase_anon.auth.reset_password_for_email(
            data.email,
            {
                "redirect_to": redirect_to,
            },
        )
        return {"message": "Ссылка для сброса пароля отправлена на ваш email."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка сброса пароля: {str(e)}")
