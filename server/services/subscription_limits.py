from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from database import supabase


BISHKEK_TZ = ZoneInfo("Asia/Bishkek")
DAILY_LIMITS = {
    "day": 3,
    "week": 15,
    "month": 20,
    "quarter": 15,
}


def get_daily_limit(period: Optional[str]) -> Optional[int]:
    if not period:
        return None
    return DAILY_LIMITS.get(period)


def get_bishkek_day_bounds_utc(now: Optional[datetime] = None) -> tuple[str, str]:
    current_utc = now or datetime.now(timezone.utc)
    current_local = current_utc.astimezone(BISHKEK_TZ)
    day_start_local = current_local.replace(hour=0, minute=0, second=0, microsecond=0)
    next_day_local = day_start_local + timedelta(days=1)
    day_start_utc = day_start_local.astimezone(timezone.utc).isoformat()
    next_day_utc = next_day_local.astimezone(timezone.utc).isoformat()
    return day_start_utc, next_day_utc


def get_daily_views_used(*, employer_id: str, subscription_id: str) -> int:
    day_start_utc, next_day_utc = get_bishkek_day_bounds_utc()
    response = (
        supabase.table("card_views")
        .select("id", count="exact")
        .eq("employer_id", employer_id)
        .eq("subscription_id", subscription_id)
        .gte("viewed_at", day_start_utc)
        .lt("viewed_at", next_day_utc)
        .execute()
    )
    return int(response.count or 0)


def enrich_subscription(subscription: dict) -> dict:
    tariff = subscription.get("tariff_plans") or {}
    daily_limit = get_daily_limit(tariff.get("period"))
    daily_views_used = 0
    daily_views_remaining = None

    if daily_limit is not None:
        daily_views_used = get_daily_views_used(
            employer_id=subscription["employer_id"],
            subscription_id=subscription["id"],
        )
        daily_views_remaining = max(
            min(subscription["cards_remaining"], daily_limit - daily_views_used),
            0,
        )

    return {
        **subscription,
        "daily_limit": daily_limit,
        "daily_views_used": daily_views_used,
        "daily_views_remaining": daily_views_remaining,
    }
