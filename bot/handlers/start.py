import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from database import (
    get_bot_user_settings,
    get_employee_by_telegram_id,
    update_employee,
    upsert_bot_user_settings,
)
from i18n import language_name, resolve_language, tr


def build_language_keyboard(language: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="set_language:ru"),
            InlineKeyboardButton("🇰🇬 Кыргызча", callback_data="set_language:ky"),
        ],
        [InlineKeyboardButton(tr(language, "btn_help"), callback_data="show_help")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_start_keyboard(language: str, *, is_registered: bool) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(tr(language, "btn_help"), callback_data="show_help")]]
    if not is_registered:
        keyboard.insert(0, [InlineKeyboardButton(tr(language, "btn_register"), callback_data="start_registration")])
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.effective_message:
        return

    existing = await asyncio.to_thread(get_employee_by_telegram_id, user.id)
    user_settings = await asyncio.to_thread(get_bot_user_settings, user.id)
    language = resolve_language(
        context_language=context.user_data.get("bot_language"),
        stored_language=(existing.get("preferred_language") if existing else None) or (user_settings.get("preferred_language") if user_settings else None),
        telegram_language=user.language_code,
    )
    context.user_data["bot_language"] = language

    if existing:
        await update.effective_message.reply_text(
            tr(language, "start_registered_intro", name=existing["full_name"]),
            reply_markup=build_start_keyboard(language, is_registered=True),
        )
        return

    if not user_settings or not user_settings.get("language_selected"):
        await update.effective_message.reply_text(
            tr(language, "start_intro", name=user.first_name or "друг"),
            reply_markup=build_language_keyboard(language),
        )
        return

    await update.effective_message.reply_text(
        tr(language, "start_returning", name=user.first_name or "друг"),
        reply_markup=build_start_keyboard(language, is_registered=False),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.effective_message:
        return

    existing = await asyncio.to_thread(get_employee_by_telegram_id, user.id)
    user_settings = await asyncio.to_thread(get_bot_user_settings, user.id)
    language = resolve_language(
        context_language=context.user_data.get("bot_language"),
        stored_language=(existing.get("preferred_language") if existing else None) or (user_settings.get("preferred_language") if user_settings else None),
        telegram_language=user.language_code,
    )
    context.user_data["bot_language"] = language
    await update.effective_message.reply_text(tr(language, "help_text"))


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or not update.effective_message:
        return

    existing = await asyncio.to_thread(get_employee_by_telegram_id, user.id)
    user_settings = await asyncio.to_thread(get_bot_user_settings, user.id)
    language = resolve_language(
        context_language=context.user_data.get("bot_language"),
        stored_language=(existing.get("preferred_language") if existing else None) or (user_settings.get("preferred_language") if user_settings else None),
        telegram_language=user.language_code,
    )
    context.user_data["bot_language"] = language
    await update.effective_message.reply_text(
        tr(language, "language_choose"),
        reply_markup=build_language_keyboard(language),
    )


async def set_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()
    _, language = query.data.split(":", 1)
    context.user_data["bot_language"] = language

    employee = await asyncio.to_thread(get_employee_by_telegram_id, query.from_user.id)
    await asyncio.to_thread(
        upsert_bot_user_settings,
        query.from_user.id,
        {
            "preferred_language": language,
            "language_selected": True,
        },
    )
    if employee:
        await asyncio.to_thread(update_employee, query.from_user.id, {"preferred_language": language})

    is_registered = bool(employee)
    name = employee.get("full_name") if employee else (query.from_user.first_name or "друг")

    await query.edit_message_text(
        f"{tr(language, 'language_changed', language_label=language_name(language))}\n\n"
        f"{tr(language, 'start_registered_intro' if is_registered else 'start_returning', name=name)}",
        reply_markup=build_start_keyboard(language, is_registered=is_registered),
    )


async def start_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()
    existing = await asyncio.to_thread(get_employee_by_telegram_id, query.from_user.id)
    user_settings = await asyncio.to_thread(get_bot_user_settings, query.from_user.id)
    language = resolve_language(
        context_language=context.user_data.get("bot_language"),
        stored_language=(existing.get("preferred_language") if existing else None) or (user_settings.get("preferred_language") if user_settings else None),
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
