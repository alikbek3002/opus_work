from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from activity_signal import format_employee_activity_status
from database import delete_employee, get_employee_by_telegram_id


def build_profile_actions_keyboard() -> InlineKeyboardMarkup:
    """Кнопки управления уже сохранённой анкетой."""
    keyboard = [
        [InlineKeyboardButton("🗑 Удалить анкету", callback_data="request_delete_profile")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_delete_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение удаления анкеты."""
    keyboard = [
        [InlineKeyboardButton("✅ Да, удалить", callback_data="confirm_delete_profile")],
        [InlineKeyboardButton("↩️ Нет, оставить", callback_data="cancel_delete_profile")],
    ]
    return InlineKeyboardMarkup(keyboard)


def format_telegram_username(username: str | None) -> str:
    if not username:
        return "Не указан"
    return f"@{username.lstrip('@')}"


def format_contact_method(employee: dict) -> str:
    return "WhatsApp" if employee.get("has_whatsapp") else "Обычный номер"


def format_yes_no(value: bool | None) -> str:
    if value is None:
        return "Не указано"
    return "Да" if value else "Нет"


def format_photo_status(photo_file_id: str | None) -> str:
    return "Загружено ✅" if photo_file_id else "Не загружено"


def derive_weekend_from_schedule(schedule: str | None, ready_for_weekends: bool | None) -> bool | None:
    if ready_for_weekends is not None:
        return ready_for_weekends
    if not schedule:
        return None
    normalized = schedule.lower()
    if "выход" in normalized:
        return True
    if "будни" in normalized:
        return False
    return None


def get_verification_status_text(employee: dict) -> tuple[str, str]:
    status = employee.get("verification_status")
    if status == "verified" or employee.get("is_verified"):
        return "Полностью верифицирован", "✅"
    if status == "rejected":
        return "Отклонён модератором", "❌"
    return "Ожидает ручной проверки", "⏳"


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отображает текущий профиль пользователя."""
    telegram_id = update.effective_user.id
    employee = get_employee_by_telegram_id(telegram_id)

    if not employee:
        await update.message.reply_text("❌ Вы ещё не зарегистрированы. Напишите /start")
        return

    status_text, status_emoji = get_verification_status_text(employee)
    activity_status = format_employee_activity_status(employee)
    activity_status_text = f"{escape(activity_status)}\n" if activity_status else ""

    text = (
        "👤 <b>Ваш профиль</b>\n\n"
        f"Имя: {escape(str(employee.get('full_name', 'Не указано')))}\n"
        f"Возраст: {escape(str(employee.get('age', 'Не указано')))}\n"
        f"Пол: {escape(str(employee.get('gender', 'Не указано')))}\n"
        f"Фото: {escape(format_photo_status(employee.get('photo_file_id')))}\n"
        f"Район: {escape(str(employee.get('district', 'Не указано')))}\n"
        f"Профессия: {escape(str(employee.get('specializations', 'Не указано')))}\n"
        f"Где работал(а): {escape(str(employee.get('experience', 'Не указано')))}\n"
        f"Занятость: {escape(str(employee.get('employment_type', 'Не указано')))}\n"
        f"График: {escape(str(employee.get('schedule', 'Не указано')))}\n"
        f"Готов(а) к выходным: {escape(format_yes_no(derive_weekend_from_schedule(employee.get('schedule'), employee.get('ready_for_weekends'))))}\n"
        f"Сан. книжка: {escape(str(employee.get('has_sanitary_book', 'Не указано')))}\n"
        f"О себе: {escape(str(employee.get('about_me', 'Не указано')))}\n"
        f"Есть рекомендации: {escape(format_yes_no(employee.get('has_recommendations')))}\n"
        f"Telegram username: {escape(format_telegram_username(employee.get('telegram_username')))}\n"
        f"Связь: {escape(format_contact_method(employee))}\n"
        f"Номер: {escape(str(employee.get('phone_number', 'Не указан')))}\n\n"
        f"{activity_status_text}"
        f"Статус: {status_text} {status_emoji}\n\n"
        "После отправки анкеты изменения делаются через удаление и повторное заполнение."
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=build_profile_actions_keyboard(),
    )


async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Объясняет, как обновить уже сохранённую анкету."""
    telegram_id = update.effective_user.id
    employee = get_employee_by_telegram_id(telegram_id)

    if not employee:
        await update.message.reply_text("❌ Вы ещё не зарегистрированы. Напишите /start")
        return

    await update.message.reply_text(
        "После отправки анкеты редактирование делается так:\n"
        "1. Удаляете текущую анкету.\n"
        "2. Проходите регистрацию заново.\n\n"
        "Если готовы, нажмите кнопку ниже.",
        reply_markup=build_profile_actions_keyboard(),
    )


async def request_delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запрашивает подтверждение удаления анкеты."""
    query = update.callback_query
    await query.answer()

    employee = get_employee_by_telegram_id(query.from_user.id)
    if not employee:
        await query.edit_message_text("❌ Анкета уже удалена. Напишите /start, чтобы зарегистрироваться заново.")
        return

    await query.edit_message_text(
        "⚠️ Вы действительно хотите удалить свою анкету?\n"
        "После удаления нужно будет пройти регистрацию заново.",
        reply_markup=build_delete_confirmation_keyboard(),
    )


async def confirm_delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Удаляет анкету пользователя."""
    query = update.callback_query
    await query.answer()

    delete_employee(query.from_user.id)
    
    # Пытаемся удалить фото из Railway (даже если его там нет, ошибка не прервёт процесс, если обработать или просто вызвать)
    try:
        from photo_storage import delete_photo
        delete_photo(query.from_user.id)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Не удалось удалить фото: %s", e)
        
    context.user_data.clear()

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📝 Пройти регистрацию заново", callback_data="start_registration")]]
    )

    await query.edit_message_text(
        "✅ Ваша анкета удалена.\n"
        "Нажмите кнопку ниже, чтобы заполнить её заново.",
        reply_markup=reply_markup,
    )


async def cancel_delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отменяет удаление анкеты."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Анкета не удалена.\n"
        "Используйте /profile, чтобы посмотреть профиль.",
    )


def get_profile_handlers() -> list:
    """Возвращает список хендлеров для профиля."""
    return [
        CommandHandler("profile", profile_command),
        CommandHandler("update", update_command),
        CallbackQueryHandler(request_delete_profile, pattern="^request_delete_profile$"),
        CallbackQueryHandler(confirm_delete_profile, pattern="^confirm_delete_profile$"),
        CallbackQueryHandler(cancel_delete_profile, pattern="^cancel_delete_profile$"),
    ]
