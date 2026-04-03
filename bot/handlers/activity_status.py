from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from activity_signal import get_activity_signal_meta
from database import get_employee_by_telegram_id, update_employee_activity_signal
from i18n import resolve_language, tr


async def activity_signal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if not query.data:
        return

    _, signal = query.data.split(":", 1)
    employee = get_employee_by_telegram_id(query.from_user.id)
    language = resolve_language(
        context_language=context.user_data.get("bot_language"),
        stored_language=employee.get("preferred_language") if employee else None,
        telegram_language=query.from_user.language_code,
    )
    context.user_data["bot_language"] = language

    if not employee:
        await query.edit_message_text(
            tr(language, "activity_missing_profile")
        )
        return

    meta = get_activity_signal_meta(employee.get("employment_type"), signal, language)
    if not meta:
        await query.answer(tr(language, "activity_unknown_option"), show_alert=True)
        return

    updated_employee = update_employee_activity_signal(query.from_user.id, signal)
    if not updated_employee:
        await query.answer(tr(language, "activity_save_error"), show_alert=True)
        return

    await query.edit_message_text(
        tr(language, "activity_saved", title=meta["title"], label=meta["label"])
    )


def get_activity_status_handlers() -> list:
    return [
        CallbackQueryHandler(activity_signal_callback, pattern=r"^activity_signal:(high|medium|low)$"),
    ]
