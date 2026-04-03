from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

from database import get_employee_by_telegram_id


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    telegram_id = user.id

    # Проверяем, зарегистрирован ли уже пользователь
    existing = get_employee_by_telegram_id(telegram_id)

    if existing:
        await update.message.reply_text(
            f"👋 Привет, {existing['full_name']}!\n\n"
            f"Вы уже зарегистрированы в системе OPUS Анкеты.\n"
            f"Используйте /profile чтобы посмотреть ваш профиль\n"
            f"или /update чтобы удалить анкету и заполнить её заново."
        )
        return

    keyboard = [
        [InlineKeyboardButton("📝 Зарегистрироваться", callback_data="start_registration")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Здравствуйте, {user.first_name}!\n\n"
        f"Добро пожаловать в *OPUS Анкеты* — платформу для поиска работы.\n\n"
        f"Зарегистрируйте своё резюме, чтобы работодатели могли найти вас.\n"
        f"Нажмите кнопку ниже, чтобы начать регистрацию.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


def get_start_handler() -> CommandHandler:
    """Возвращает хендлер для команды /start."""
    return CommandHandler("start", start_command)
