from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from database import get_employee_by_telegram_id, update_employee
from i18n import language_name, resolve_language, tr


def build_language_keyboard(language: str, *, is_registered: bool) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Русский", callback_data="set_language:ru"),
            InlineKeyboardButton("Кыргызча", callback_data="set_language:ky"),
        ],
        [InlineKeyboardButton(tr(language, "btn_help"), callback_data="show_help")],
    ]
    if not is_registered:
        keyboard.insert(1, [InlineKeyboardButton(tr(language, "btn_register"), callback_data="start_registration")])
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.effective_message:
        return

    existing = get_employee_by_telegram_id(user.id)
    language = resolve_language(
        context_language=context.user_data.get("bot_language"),
        stored_language=existing.get("preferred_language") if existing else None,
        telegram_language=user.language_code,
    )
    context.user_data["bot_language"] = language

    if existing:
        await update.effective_message.reply_text(
            tr(language, "start_registered_intro", name=existing["full_name"]),
            reply_markup=build_language_keyboard(language, is_registered=True),
        )
        return

    await update.effective_message.reply_text(
        tr(language, "start_intro", name=user.first_name or "друг"),
        reply_markup=build_language_keyboard(language, is_registered=False),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.effective_message:
        return

    existing = get_employee_by_telegram_id(user.id)
    language = resolve_language(
        context_language=context.user_data.get("bot_language"),
        stored_language=existing.get("preferred_language") if existing else None,
        telegram_language=user.language_code,
    )
    context.user_data["bot_language"] = language
    await update.effective_message.reply_text(tr(language, "help_text"))


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.effective_message:
        return

    existing = get_employee_by_telegram_id(user.id)
    language = resolve_language(
        context_language=context.user_data.get("bot_language"),
        stored_language=existing.get("preferred_language") if existing else None,
        telegram_language=user.language_code,
    )
    context.user_data["bot_language"] = language
    await update.effective_message.reply_text(
        tr(language, "language_choose"),
        reply_markup=build_language_keyboard(language, is_registered=bool(existing)),
    )


async def set_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()
    _, language = query.data.split(":", 1)
    context.user_data["bot_language"] = language

    employee = get_employee_by_telegram_id(query.from_user.id)
    if employee:
        update_employee(query.from_user.id, {"preferred_language": language})

    is_registered = bool(employee)
    name = employee.get("full_name") if employee else (query.from_user.first_name or "друг")

    await query.edit_message_text(
        f"{tr(language, 'language_changed', language=language_name(language))}\n\n"
        f"{tr(language, 'start_registered_intro' if is_registered else 'start_intro', name=name)}",
        reply_markup=build_language_keyboard(language, is_registered=is_registered),
    )


async def start_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()
    existing = get_employee_by_telegram_id(query.from_user.id)
    language = resolve_language(
        context_language=context.user_data.get("bot_language"),
        stored_language=existing.get("preferred_language") if existing else None,
        telegram_language=query.from_user.language_code,
    )
    context.user_data["bot_language"] = language

    if query.data == "show_help":
        await query.message.reply_text(tr(language, "help_text"))
        return


def get_start_handlers() -> list:
    return [
        CommandHandler("start", start_command),
        CommandHandler("help", help_command),
        CommandHandler("language", language_command),
        CallbackQueryHandler(set_language_callback, pattern="^set_language:(ru|ky)$"),
        CallbackQueryHandler(start_menu_callback, pattern="^show_help$"),
    ]
