import logging
from telegram.ext import ApplicationBuilder

from config import settings
from handlers.start import get_start_handler
from handlers.registration import get_registration_handler
from handlers.profile import get_profile_handlers

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """Запуск бота."""
    settings.validate()

    app = ApplicationBuilder().token(settings.BOT_TOKEN).build()

    # Регистрируем хендлеры
    app.add_handler(get_registration_handler())  # ConversationHandler (приоритетнее)
    app.add_handler(get_start_handler())
    for handler in get_profile_handlers():
        app.add_handler(handler)

    logger.info("🤖 Opus Bot запущен!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
