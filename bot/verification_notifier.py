from html import escape
import logging

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from config import settings
from database import supabase

logger = logging.getLogger(__name__)


def _format_value(value, fallback: str = "Не указано") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def _build_employee_message(employee: dict) -> str:
    full_name = escape(_format_value(employee.get("full_name")))
    specializations = escape(_format_value(employee.get("specializations")))
    district = escape(_format_value(employee.get("district")))
    age = escape(_format_value(employee.get("age")))
    gender = escape(_format_value(employee.get("gender")))
    experience = escape(_format_value(employee.get("experience")))
    employment_type = escape(_format_value(employee.get("employment_type")))
    phone_number = escape(_format_value(employee.get("phone_number"), "Не указан"))
    about_me = escape(_format_value(employee.get("about_me")))
    telegram_username = employee.get("telegram_username")
    telegram_link = (
        f"@{escape(str(telegram_username).lstrip('@'))}"
        if telegram_username
        else "Не указан"
    )
    has_whatsapp = "Да" if employee.get("has_whatsapp") else "Нет"

    return (
        "🆕 <b>Новая анкета на ручную проверку</b>\n\n"
        f"ID: <code>{escape(_format_value(employee.get('id')))}</code>\n"
        f"Имя: {full_name}\n"
        f"Возраст: {age}\n"
        f"Пол: {gender}\n"
        f"Профессия: {specializations}\n"
        f"Район: {district}\n"
        f"Опыт: {experience}\n"
        f"Занятость: {employment_type}\n"
        f"WhatsApp: {has_whatsapp}\n"
        f"Telegram: {telegram_link}\n"
        f"Телефон: {phone_number}\n"
        f"О себе: {about_me}"
    )


def _build_keyboard(employee_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Верифицировать",
                    callback_data=f"verify:{employee_id}",
                ),
                InlineKeyboardButton(
                    "❌ Отклонить",
                    callback_data=f"reject:{employee_id}",
                ),
            ]
        ]
    )


async def notify_new_employee(employee: dict) -> None:
    if not settings.VERIFICATION_BOT_TOKEN:
        return

    employee_id = employee.get("id")
    if not employee_id:
        logger.warning("Не удалось отправить анкету на модерацию: отсутствует employee.id")
        return

    subscribers_response = (
        supabase.table("verification_bot_subscribers")
        .select("chat_id")
        .eq("is_active", True)
        .execute()
    )
    subscribers = subscribers_response.data or []
    if not subscribers:
        logger.info("Нет подписчиков verification bot для рассылки анкеты %s", employee_id)
        return

    bot = Bot(token=settings.VERIFICATION_BOT_TOKEN)
    message_text = _build_employee_message(employee)
    reply_markup = _build_keyboard(str(employee_id))

    for subscriber in subscribers:
        chat_id = subscriber.get("chat_id")
        if not chat_id:
            continue

        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message_text,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        except Exception as exc:
            error_text = str(exc).lower()
            if any(fragment in error_text for fragment in ["blocked", "chat not found", "user is deactivated", "forbidden"]):
                supabase.table("verification_bot_subscribers").update(
                    {"is_active": False}
                ).eq("chat_id", chat_id).execute()
            logger.warning(
                "Не удалось отправить анкету %s в чат %s: %s",
                employee_id,
                chat_id,
                exc,
            )
