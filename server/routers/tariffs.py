from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from config import settings
from database import supabase
from middleware.auth import get_current_user
from models.schemas import TariffPlan, SubscriptionDetails
from services.email import email_is_configured, send_email

router = APIRouter(prefix="/api/tariffs", tags=["Тарифные планы"])


@router.get("", response_model=List[TariffPlan])
async def get_tariffs():
    """Получить список доступных тарифных планов."""
    response = (
        supabase.table("tariff_plans")
        .select("*")
        .eq("is_active", True)
        .order("price")
        .execute()
    )
    return response.data


@router.get("/subscription", response_model=Optional[SubscriptionDetails])
async def get_subscription(current_user: dict = Depends(get_current_user)):
    """Получить текущую активную подписку работодателя."""
    now_iso = datetime.utcnow().isoformat()
    response = (
        supabase.table("subscriptions")
        .select("*, tariff_plans(*)")
        .eq("employer_id", current_user["id"])
        .eq("is_active", True)
        .gt("expires_at", now_iso)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]
    return None


@router.post("/notify-expiring")
async def notify_expiring_subscriptions(
    x_cron_token: Optional[str] = Header(default=None),
):
    """Отправить email-напоминания по истекающим подпискам."""
    if not settings.CRON_SECRET:
        raise HTTPException(status_code=500, detail="CRON_SECRET не настроен")
    if x_cron_token != settings.CRON_SECRET:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    if not email_is_configured():
        raise HTTPException(status_code=500, detail="SMTP не настроен")

    now = datetime.utcnow()
    now_iso = now.isoformat()
    three_days_later_iso = (now + timedelta(days=3)).isoformat()

    sent = 0
    skipped = 0
    deactivated = 0

    expired_response = (
        supabase.table("subscriptions")
        .select("id, employer_id, expires_at, employers(email, full_name, company_name), tariff_plans(name, period)")
        .eq("is_active", True)
        .lte("expires_at", now_iso)
        .execute()
    )

    for subscription in expired_response.data or []:
        supabase.table("subscriptions").update({"is_active": False}).eq("id", subscription["id"]).execute()
        deactivated += 1

        employer = subscription.get("employers") or {}
        email = employer.get("email")
        if not email:
            skipped += 1
            continue

        existing = (
            supabase.table("subscription_notifications")
            .select("id")
            .eq("subscription_id", subscription["id"])
            .eq("notification_type", "expired")
            .limit(1)
            .execute()
        )
        if existing.data:
            skipped += 1
            continue

        tariff = subscription.get("tariff_plans") or {}
        subject = "Подписка Opus завершилась"
        text_body = (
            f"Здравствуйте, {employer.get('full_name') or employer.get('company_name') or 'партнер'}!\n\n"
            f"Ваша подписка на тариф «{tariff.get('name', 'Opus')}» завершилась.\n"
            f"Чтобы продолжить открывать контакты сотрудников, продлите доступ: {settings.APP_URL}/tariffs\n"
        )
        html_body = (
            f"<p>Здравствуйте, {employer.get('full_name') or employer.get('company_name') or 'партнер'}!</p>"
            f"<p>Ваша подписка на тариф <strong>{tariff.get('name', 'Opus')}</strong> завершилась.</p>"
            f"<p><a href='{settings.APP_URL}/tariffs'>Продлить доступ в Opus</a></p>"
        )
        send_email(email, subject, text_body, html_body)
        supabase.table("subscription_notifications").insert({
            "employer_id": subscription["employer_id"],
            "subscription_id": subscription["id"],
            "notification_type": "expired",
        }).execute()
        sent += 1

    upcoming_response = (
        supabase.table("subscriptions")
        .select("id, employer_id, expires_at, employers(email, full_name, company_name), tariff_plans(name, period)")
        .eq("is_active", True)
        .gt("expires_at", now_iso)
        .lte("expires_at", three_days_later_iso)
        .execute()
    )

    for subscription in upcoming_response.data or []:
        employer = subscription.get("employers") or {}
        email = employer.get("email")
        if not email:
            skipped += 1
            continue

        expires_at = datetime.fromisoformat(subscription["expires_at"].replace("Z", "+00:00"))
        hours_left = max((expires_at.replace(tzinfo=None) - now).total_seconds() / 3600, 0)
        notification_type = "expiring_1d" if hours_left <= 24 else "expiring_3d"

        existing = (
            supabase.table("subscription_notifications")
            .select("id")
            .eq("subscription_id", subscription["id"])
            .eq("notification_type", notification_type)
            .limit(1)
            .execute()
        )
        if existing.data:
            skipped += 1
            continue

        tariff = subscription.get("tariff_plans") or {}
        days_label = "24 часов" if notification_type == "expiring_1d" else "3 дня"
        subject = "Подписка Opus скоро закончится"
        text_body = (
            f"Здравствуйте, {employer.get('full_name') or employer.get('company_name') or 'партнер'}!\n\n"
            f"Ваша подписка на тариф «{tariff.get('name', 'Opus')}» закончится примерно через {days_label}.\n"
            f"Чтобы не потерять доступ к контактам сотрудников, продлите тариф заранее: {settings.APP_URL}/tariffs\n"
        )
        html_body = (
            f"<p>Здравствуйте, {employer.get('full_name') or employer.get('company_name') or 'партнер'}!</p>"
            f"<p>Ваша подписка на тариф <strong>{tariff.get('name', 'Opus')}</strong> закончится примерно через <strong>{days_label}</strong>.</p>"
            f"<p><a href='{settings.APP_URL}/tariffs'>Продлить доступ заранее</a></p>"
        )
        send_email(email, subject, text_body, html_body)
        supabase.table("subscription_notifications").insert({
            "employer_id": subscription["employer_id"],
            "subscription_id": subscription["id"],
            "notification_type": notification_type,
        }).execute()
        sent += 1

    return {
        "status": "ok",
        "sent": sent,
        "skipped": skipped,
        "deactivated": deactivated,
    }
