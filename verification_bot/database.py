from datetime import datetime, timezone

from supabase import Client, create_client

from config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def upsert_subscriber(
    *,
    chat_id: int,
    chat_type: str | None,
    user_id: int | None,
    username: str | None,
    full_name: str | None,
) -> None:
    supabase.table("verification_bot_subscribers").upsert(
        {
            "chat_id": chat_id,
            "chat_type": chat_type,
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "is_active": True,
            "last_seen_at": datetime.now(timezone.utc).isoformat(),
        },
        on_conflict="chat_id",
    ).execute()


def list_active_subscribers() -> list[dict]:
    response = (
        supabase.table("verification_bot_subscribers")
        .select("*")
        .eq("is_active", True)
        .execute()
    )
    return response.data or []


def deactivate_subscriber(chat_id: int) -> None:
    supabase.table("verification_bot_subscribers").update(
        {
            "is_active": False,
            "last_seen_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("chat_id", chat_id).execute()


def list_pending_employees(limit: int = 20) -> list[dict]:
    response = (
        supabase.table("employees")
        .select("*")
        .eq("verification_status", "pending")
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return response.data or []


def get_employee_by_id(employee_id: str) -> dict | None:
    response = (
        supabase.table("employees")
        .select("*")
        .eq("id", employee_id)
        .limit(1)
        .execute()
    )
    if response.data:
        return response.data[0]
    return None


def update_employee_verification(employee_id: str, status: str, moderator_telegram_id: int) -> dict | None:
    response = (
        supabase.table("employees")
        .update(
            {
                "verification_status": status,
                "verified_by_telegram_id": moderator_telegram_id,
                "verification_decided_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        .eq("id", employee_id)
        .execute()
    )
    if response.data:
        return response.data[0]
    return None
