from datetime import datetime, timezone

from supabase import create_client, Client
from config import settings
from activity_signal import FULL_TIME_EMPLOYMENT, PART_TIME_EMPLOYMENT, is_activity_prompt_due

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def save_employee(data: dict) -> dict:
    """Сохраняет или обновляет данные сотрудника в базу данных."""
    response = (
        supabase.table("employees")
        .upsert(data, on_conflict="telegram_id")
        .execute()
    )
    return response.data[0] if response.data else {}


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


def list_employees_due_for_activity_prompt() -> list[dict]:
    response = (
        supabase.table("employees")
        .select("telegram_id, full_name, employment_type, activity_signal_prompted_at")
        .execute()
    )

    employees = response.data or []
    due_employees: list[dict] = []
    allowed_employment_types = {PART_TIME_EMPLOYMENT, FULL_TIME_EMPLOYMENT}

    for employee in employees:
        if not employee.get("telegram_id"):
            continue
        if employee.get("employment_type") not in allowed_employment_types:
            continue
        if not is_activity_prompt_due(employee.get("activity_signal_prompted_at")):
            continue
        due_employees.append(employee)

    return due_employees


def mark_activity_prompt_sent(telegram_id: int) -> dict:
    response = (
        supabase.table("employees")
        .update({"activity_signal_prompted_at": datetime.now(timezone.utc).isoformat()})
        .eq("telegram_id", telegram_id)
        .execute()
    )
    return response.data


def update_employee_activity_signal(telegram_id: int, signal: str) -> dict | None:
    now_iso = datetime.now(timezone.utc).isoformat()
    response = (
        supabase.table("employees")
        .update(
            {
                "activity_signal": signal,
                "activity_signal_updated_at": now_iso,
                "activity_signal_prompted_at": now_iso,
            }
        )
        .eq("telegram_id", telegram_id)
        .execute()
    )
    return response.data[0] if response.data else None


def delete_employee(telegram_id: int) -> dict:
    """Удаляет анкету сотрудника по Telegram ID."""
    response = (
        supabase.table("employees")
        .delete()
        .eq("telegram_id", telegram_id)
        .execute()
    )
    return response.data
