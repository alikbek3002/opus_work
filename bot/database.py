from supabase import create_client, Client
from config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def save_employee(data: dict) -> dict:
    """Сохраняет или обновляет данные сотрудника в базу данных."""
    response = (
        supabase.table("employees")
        .upsert(data, on_conflict="telegram_id")
        .execute()
    )
    return response.data


def get_employee_by_telegram_id(telegram_id: int) -> dict | None:
    """Проверяет, зарегистрирован ли сотрудник."""
    response = (
        supabase.table("employees")
        .select("*")
        .eq("telegram_id", telegram_id)
        .execute()
    )
    if response.data:
        return response.data[0]
    return None


def update_employee(telegram_id: int, data: dict) -> dict:
    """Обновляет данные сотрудника."""
    response = (
        supabase.table("employees")
        .update(data)
        .eq("telegram_id", telegram_id)
        .execute()
    )
    return response.data


def delete_employee(telegram_id: int) -> dict:
    """Удаляет анкету сотрудника по Telegram ID."""
    response = (
        supabase.table("employees")
        .delete()
        .eq("telegram_id", telegram_id)
        .execute()
    )
    return response.data
