import logging
import asyncio
from contextlib import suppress

from telegram.ext import ApplicationBuilder
from telegram import BotCommand

from activity_signal import PROMPT_SCAN_INTERVAL_SECONDS, build_activity_signal_keyboard, build_activity_signal_prompt
from config import settings
from database import list_employees_due_for_activity_prompt, mark_activity_prompt_sent
from handlers.start import get_start_handler
from handlers.activity_status import get_activity_status_handlers
from handlers.registration import get_registration_handler
from handlers.profile import get_profile_handlers

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def send_due_activity_prompts(application) -> None:
    due_employees = list_employees_due_for_activity_prompt()
    if not due_employees:
        return

    for employee in due_employees:
        telegram_id = employee.get("telegram_id")
        employment_type = employee.get("employment_type")
        message_text = build_activity_signal_prompt(employee.get("full_name"), employment_type)
        reply_markup = build_activity_signal_keyboard(employment_type)

        if not telegram_id or not message_text or not reply_markup:
            continue

        try:
            await application.bot.send_message(
                chat_id=telegram_id,
                text=message_text,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        except Exception as exc:
            logger.warning("Не удалось отправить 72-часовой статус сотруднику %s: %s", telegram_id, exc)
        else:
            mark_activity_prompt_sent(int(telegram_id))

        await asyncio.sleep(0.1)


async def activity_prompt_loop(application) -> None:
    while True:
        try:
            await send_due_activity_prompts(application)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Ошибка фоновой рассылки 72-часового статуса")

        await asyncio.sleep(PROMPT_SCAN_INTERVAL_SECONDS)


async def on_post_init(application) -> None:
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("profile", "Моя анкета"),
        BotCommand("update", "Редактировать анкету"),
        BotCommand("help", "Помощь")
    ]
    await application.bot.set_my_commands(commands)
    application.bot_data["activity_prompt_task"] = asyncio.create_task(activity_prompt_loop(application))


async def on_post_shutdown(application) -> None:
    task = application.bot_data.get("activity_prompt_task")
    if not task:
        return

    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


def main():
    """Запуск бота."""
    settings.validate()
    
    # Инициализация хранилища фото
    from photo_storage import ensure_photos_table
    ensure_photos_table()

    app = (
        ApplicationBuilder()
        .token(settings.BOT_TOKEN)
        .post_init(on_post_init)
        .post_shutdown(on_post_shutdown)
        .build()
    )

    # Регистрируем хендлеры
    app.add_handler(get_registration_handler())  # ConversationHandler (приоритетнее)
    app.add_handler(get_start_handler())
    for handler in get_profile_handlers():
        app.add_handler(handler)
    for handler in get_activity_status_handlers():
        app.add_handler(handler)

    logger.info("🤖 Opus Bot запущен!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
