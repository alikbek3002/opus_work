from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from activity_signal import get_activity_signal_meta
from database import get_employee_by_telegram_id, update_employee_activity_signal


async def activity_signal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if not query.data:
        return

    _, signal = query.data.split(":", 1)
    employee = get_employee_by_telegram_id(query.from_user.id)

    if not employee:
        await query.edit_message_text(
            "Анкета не найдена. Если вы удаляли профиль, зарегистрируйтесь заново через /start."
        )
        return

    meta = get_activity_signal_meta(employee.get("employment_type"), signal)
    if not meta:
        await query.answer("Не удалось определить этот вариант ответа", show_alert=True)
        return

    updated_employee = update_employee_activity_signal(query.from_user.id, signal)
    if not updated_employee:
        await query.answer("Не удалось сохранить ответ", show_alert=True)
        return

    await query.edit_message_text(
        "Спасибо, статус обновлён.\n\n"
        f"{meta['title']}: {meta['label']}\n\n"
        "Эта информация теперь отображается в вашей анкете на сайте Opus."
    )


def get_activity_status_handlers() -> list:
    return [
        CallbackQueryHandler(activity_signal_callback, pattern=r"^activity_signal:(high|medium|low)$"),
    ]
