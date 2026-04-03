from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from database import (
    get_employee_by_id,
    list_pending_employees,
    update_employee_verification,
    upsert_subscriber,
)


def format_value(value, fallback: str = "Не указано") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def format_yes_no(value: bool | None) -> str:
    if value is None:
        return "Не указано"
    return "Да" if value else "Нет"


def derive_weekend_from_schedule(employee: dict) -> bool | None:
    ready_for_weekends = employee.get("ready_for_weekends")
    if ready_for_weekends is not None:
        return ready_for_weekends

    schedule = employee.get("schedule")
    if not schedule:
        return None

    normalized = str(schedule).lower()
    if "выход" in normalized:
        return True
    if "будни" in normalized:
        return False
    return None


def status_meta(employee: dict) -> tuple[str, str]:
    status = employee.get("verification_status")
    if status == "verified" or employee.get("is_verified"):
        return "✅", "Полностью верифицирован"
    if status == "rejected":
        return "❌", "Отклонён"
    return "⏳", "На ручной проверке"


def build_keyboard(employee_id: str) -> InlineKeyboardMarkup:
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


def build_employee_message(employee: dict) -> str:
    status_emoji, status_text = status_meta(employee)
    created_at = employee.get("created_at")
    created_at_text = escape(format_value(created_at))
    verified_by = employee.get("verified_by_telegram_id")
    verified_by_text = f"\nМодератор: <code>{verified_by}</code>" if verified_by else ""
    rejected_reason = employee.get("verification_rejected_reason")
    rejected_reason_text = (
        f"\nПричина отклонения: {escape(format_value(rejected_reason))}"
        if rejected_reason
        else ""
    )

    telegram_username = employee.get("telegram_username")
    telegram_display = (
        f"@{escape(str(telegram_username).lstrip('@'))}"
        if telegram_username
        else "Не указан"
    )

    return (
        f"{status_emoji} <b>Анкета сотрудника</b>\n\n"
        f"ID: <code>{escape(format_value(employee.get('id')))}</code>\n"
        f"Имя: {escape(format_value(employee.get('full_name')))}\n"
        f"Возраст: {escape(format_value(employee.get('age')))}\n"
        f"Пол: {escape(format_value(employee.get('gender')))}\n"
        f"Профессия: {escape(format_value(employee.get('specializations')))}\n"
        f"Район: {escape(format_value(employee.get('district')))}\n"
        f"Опыт: {escape(format_value(employee.get('experience')))}\n"
        f"Занятость: {escape(format_value(employee.get('employment_type')))}\n"
        f"График: {escape(format_value(employee.get('schedule')))}\n"
        f"Выходные: {escape(format_yes_no(derive_weekend_from_schedule(employee)))}\n"
        f"Сан. книжка: {escape(format_value(employee.get('has_sanitary_book')))}\n"
        f"Рекомендации: {escape(format_yes_no(employee.get('has_recommendations')))}\n"
        f"WhatsApp: {escape(format_yes_no(employee.get('has_whatsapp')))}\n"
        f"Telegram: {telegram_display}\n"
        f"Телефон: {escape(format_value(employee.get('phone_number'), 'Не указан'))}\n"
        f"Фото: {'Загружено' if employee.get('photo_file_id') else 'Нет'}\n"
        f"О себе: {escape(format_value(employee.get('about_me')))}\n\n"
        f"Статус: <b>{status_text}</b>\n"
        f"Создано: {created_at_text}"
        f"{verified_by_text}"
        f"{rejected_reason_text}"
    )


def remember_current_chat(update: Update) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if not chat:
        return

    full_name = None
    if user:
        full_name = " ".join(part for part in [user.first_name, user.last_name] if part).strip() or None

    upsert_subscriber(
        chat_id=chat.id,
        chat_type=getattr(chat, "type", None),
        user_id=user.id if user else None,
        username=user.username if user else None,
        full_name=full_name,
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_current_chat(update)

    await update.effective_message.reply_text(
        "Бот ручной верификации запущен.\n"
        "Этот чат подписан на новые анкеты автоматически.\n"
        "Команды:\n"
        "/pending — показать анкеты, ожидающие проверки"
    )


async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_current_chat(update)

    employees = list_pending_employees(limit=20)
    if not employees:
        await update.effective_message.reply_text("Сейчас нет анкет, ожидающих ручной проверки.")
        return

    await update.effective_message.reply_text(f"В очереди {len(employees)} анкет(ы).")

    for employee in employees:
        await update.effective_message.reply_text(
            build_employee_message(employee),
            parse_mode="HTML",
            reply_markup=build_keyboard(str(employee["id"])),
        )


async def moderation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    remember_current_chat(update)

    if not query.data or ":" not in query.data:
        await query.answer("Некорректная команда", show_alert=True)
        return

    action, employee_id = query.data.split(":", 1)
    employee = get_employee_by_id(employee_id)

    if not employee:
        await query.edit_message_text("Анкета не найдена или уже удалена.")
        return

    current_status = employee.get("verification_status") or ("verified" if employee.get("is_verified") else "pending")
    if current_status != "pending":
        await query.answer("Анкета уже обработана", show_alert=True)
        await query.edit_message_text(
            build_employee_message(employee),
            parse_mode="HTML",
        )
        return

    next_status = "verified" if action == "verify" else "rejected"
    updated_employee = update_employee_verification(employee_id, next_status, query.from_user.id)

    if not updated_employee:
        await query.answer("Не удалось обновить статус", show_alert=True)
        return

    await query.answer("Статус анкеты обновлён")
    await query.edit_message_text(
        build_employee_message(updated_employee),
        parse_mode="HTML",
    )


def get_handlers() -> list:
    return [
        CommandHandler("start", start_command),
        CommandHandler("pending", pending_command),
        CallbackQueryHandler(moderation_callback, pattern=r"^(verify|reject):"),
    ]
