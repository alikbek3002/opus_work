from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from typing import List, Optional

from database import supabase
from middleware.auth import get_current_user
from models.schemas import EmployeeCard, EmployeeFullProfile, ViewedEmployeeHistoryItem
from services.subscription_limits import get_daily_limit, get_daily_views_used

router = APIRouter(prefix="/api/employees", tags=["Анкеты"])


def normalize_filter_values(values: Optional[List[str]]) -> List[str]:
    """Очищает массив фильтров от пустых значений."""
    if not values:
        return []
    return [value.strip() for value in values if value and value.strip()]


def matches_filter(field_value: Optional[str], filters: List[str]) -> bool:
    """Проверяет, содержит ли строковое поле любой из фильтров."""
    if not filters:
        return True
    if not field_value:
        return False

    normalized_value = field_value.lower()
    return any(value.lower() in normalized_value for value in filters)


@router.get("", response_model=List[EmployeeCard])
async def get_employees(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество на странице"),
    district: Optional[List[str]] = Query(None, description="Фильтр по районам (можно передать несколько district)"),
    specialization: Optional[List[str]] = Query(None, description="Фильтр по профессиям (можно передать несколько specialization)"),
):
    """
    Получить список карточек сотрудников (базовая информация).
    Контактные данные не показываются.
    Пагинация + фильтрация. (Публичный доступ)
    """
    offset = (page - 1) * limit

    district_values = normalize_filter_values(district)
    specialization_values = normalize_filter_values(specialization)

    # NOTE:
    # Районы и специализации хранятся как строка (в т.ч. перечисления через запятую),
    # поэтому фильтруем по вхождению подстроки в Python, чтобы корректно работал множественный выбор.
    response = (
        supabase.table("employees")
        .select(
            "id, full_name, gender, age, district, specializations, experience, employment_type, schedule, opus_experience, is_verified, verification_status, verification_decided_at, activity_signal, activity_signal_updated_at, contact_opens_count, telegram_id, created_at"
        )
        .order("is_verified", desc=True)
        .order("created_at", desc=True)
        .execute()
    )
    rows = response.data or []

    filtered = [
        row
        for row in rows
        if matches_filter(row.get("district"), district_values)
        and matches_filter(row.get("specializations"), specialization_values)
    ]

    return filtered[offset:offset + limit]


@router.get("/count")
async def get_employees_count(
    district: Optional[List[str]] = Query(None),
    specialization: Optional[List[str]] = Query(None),
):
    """Общее количество сотрудников (для пагинации на фронте). (Публичный доступ)"""
    district_values = normalize_filter_values(district)
    specialization_values = normalize_filter_values(specialization)

    response = supabase.table("employees").select("id, district, specializations").execute()
    rows = response.data or []

    filtered = [
        row
        for row in rows
        if matches_filter(row.get("district"), district_values)
        and matches_filter(row.get("specializations"), specialization_values)
    ]
    return {"count": len(filtered)}


@router.get("/history", response_model=List[ViewedEmployeeHistoryItem])
async def get_view_history(
    current_user: dict = Depends(get_current_user),
):
    """История уже открытых сотрудников для работодателя."""
    history_response = (
        supabase.table("card_views")
        .select("employee_id, viewed_at")
        .eq("employer_id", current_user["id"])
        .order("viewed_at", desc=True)
        .execute()
    )

    if not history_response.data:
        return []

    employee_ids = [item["employee_id"] for item in history_response.data]
    employees_response = (
        supabase.table("employees")
        .select("*")
        .in_("id", employee_ids)
        .execute()
    )
    employees_by_id = {employee["id"]: employee for employee in employees_response.data}

    history_items = []
    for item in history_response.data:
        employee = employees_by_id.get(item["employee_id"])
        if not employee:
            continue
        history_items.append({
            **employee,
            "viewed_at": item["viewed_at"],
        })

    return history_items


@router.post("/{employee_id}/view", response_model=EmployeeFullProfile)
async def view_employee(
    employee_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Просмотреть полный профиль сотрудника.
    - Если уже просматривали — возвращаем бесплатно
    - Иначе: проверяем подписку, списываем карточку, записываем просмотр
    """
    employer_id = current_user["id"]

    # 1. Проверяем, был ли уже просмотр (бесплатно если уже просмотрен)
    existing_view = (
        supabase.table("card_views")
        .select("id")
        .eq("employer_id", employer_id)
        .eq("employee_id", employee_id)
        .limit(1)
        .execute()
    )

    # 2. Получаем полные данные сотрудника безопасно (без .single(), чтобы не падать в 500)
    employee_response = (
        supabase.table("employees")
        .select("*")
        .eq("id", employee_id)
        .limit(1)
        .execute()
    )
    employee = employee_response.data[0] if employee_response.data else None

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Сотрудник не найден или анкета была обновлена. Обновите список анкет."
        )

    if existing_view.data:
        # Уже просмотрен — возвращаем без списания
        return employee

    # 3. Ищем активную подписку с оставшимися карточками
    now_iso = datetime.utcnow().isoformat()
    subscription = (
        supabase.table("subscriptions")
        .select("*, tariff_plans(period)")
        .eq("employer_id", employer_id)
        .eq("is_active", True)
        .gt("cards_remaining", 0)
        .gt("expires_at", now_iso)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not subscription.data:
        raise HTTPException(
            status_code=403,
            detail="Нет активной подписки или карточки закончились. Приобретите тарифный план."
        )

    sub = subscription.data[0]
    stored_daily_limit = sub.get("daily_limit")
    daily_limit = (
        int(stored_daily_limit)
        if isinstance(stored_daily_limit, int)
        else get_daily_limit((sub.get("tariff_plans") or {}).get("period"))
    )

    if daily_limit is not None:
        daily_views_used = get_daily_views_used(
            employer_id=employer_id,
            subscription_id=sub["id"],
        )
        daily_remaining = daily_limit - daily_views_used
        if daily_remaining <= 0:
            raise HTTPException(
                status_code=403,
                detail=f"Вы достигли дневного лимита просмотров: {daily_limit} в день. Попробуйте снова завтра.",
            )

    # 4. Списываем карточку из подписки
    new_remaining = sub["cards_remaining"] - 1
    update_data = {"cards_remaining": new_remaining}

    # Если карточки закончились — деактивируем подписку
    if new_remaining <= 0:
        update_data["is_active"] = False

    supabase.table("subscriptions").update(
        update_data
    ).eq("id", sub["id"]).execute()

    # 5. Записываем просмотр
    supabase.table("card_views").insert({
        "employer_id": employer_id,
        "employee_id": employee_id,
        "subscription_id": sub["id"],
    }).execute()

    return employee


@router.get("/viewed")
async def get_viewed_employees(
    current_user: dict = Depends(get_current_user),
):
    """Список ID сотрудников, которых работодатель уже просматривал."""
    response = (
        supabase.table("card_views")
        .select("employee_id")
        .eq("employer_id", current_user["id"])
        .execute()
    )

    viewed_ids = [item["employee_id"] for item in response.data]
    return {"viewed_ids": viewed_ids}
