import logging

from telegram.ext import ApplicationBuilder

from config import settings
from handlers import get_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    settings.validate()

    app = ApplicationBuilder().token(settings.VERIFICATION_BOT_TOKEN).build()

    for handler in get_handlers():
        app.add_handler(handler)

    logger.info("Verification bot started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
