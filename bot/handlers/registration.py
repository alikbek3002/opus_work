from html import escape

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from database import get_employee_by_telegram_id, save_employee

# Состояния диалога
(
    FULL_NAME,
    AGE,
    GENDER,
    PHOTO,
    SPECIALIZATIONS,
    EXPERIENCE,
    DISTRICT,
    EMPLOYMENT_TYPE,
    WEEKEND_WORK,
    ABOUT_ME,
    HAS_RECOMMENDATIONS,
    CONTACT_METHOD,
    PHONE_NUMBER,
    CONFIRM,
) = range(14)

CONTACT_METHOD_OPTIONS = ["WhatsApp", "Обычный номер"]
GENDER_OPTIONS = ["Мужчина", "Женщина"]
DISTRICT_OPTIONS = [
    "Бишкек",
    "ЦУМ",
    "Филармония",
    "Тунгуч",
    "Микрорайоны",
    "Джал",
    "Кызыл-Аскер",
    "Аламединский рынок",
    "Лебединовка",
    "Кок-Джар",
    "Орто-Сай село",
    "Ош базар",
    "Чон-Арык",
    "Моссовет",
]
SPECIALIZATION_OPTIONS = [
    "Посудомойщик(ца)",
    "Уборщик(ца)",
    "Повар(иха)",
    "Официант(ка)",
    "Бармен",
    "Бариста",
    "Кассир",
    "Продавец",
    "Кухработник",
    "Хостес",
    "Администратор",
    "Курьер",
]
EMPLOYMENT_TYPE_OPTIONS = ["Полная занятость", "Подработка"]
YES_NO_OPTIONS = ["Да", "Нет"]
FIELD_LABELS = {
    "full_name": "Имя",
    "age": "Возраст",
    "gender": "Пол",
    "photo_file_id": "Фото",
    "specializations": "Профессия",
    "experience": "Опыт работы",
    "district": "Район",
    "employment_type": "Занятость",
    "ready_for_weekends": "Готовность работать в выходные",
    "about_me": "О себе",
    "has_recommendations": "Рекомендации",
    "has_whatsapp": "Способ связи",
    "phone_number": "Номер телефона",
}


def build_reply_keyboard(options: list[str], columns: int = 2) -> ReplyKeyboardMarkup:
    """Строит клавиатуру выбора с кнопками."""
    rows = [options[index:index + columns] for index in range(0, len(options), columns)]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)


def build_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения анкеты."""
    keyboard = [
        [InlineKeyboardButton("✅ Отправить анкету", callback_data="confirm_registration")],
        [InlineKeyboardButton("✏️ Редактировать", callback_data="edit_registration")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_registration")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_edit_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования."""
    keyboard = [
        [
            InlineKeyboardButton("👤 Имя", callback_data="edit_field:full_name"),
            InlineKeyboardButton("🎂 Возраст", callback_data="edit_field:age"),
        ],
        [
            InlineKeyboardButton("⚧ Пол", callback_data="edit_field:gender"),
            InlineKeyboardButton("📷 Фото", callback_data="edit_field:photo_file_id"),
        ],
        [
            InlineKeyboardButton("🧰 Профессия", callback_data="edit_field:specializations"),
            InlineKeyboardButton("💼 Опыт", callback_data="edit_field:experience"),
        ],
        [
            InlineKeyboardButton("📍 Район", callback_data="edit_field:district"),
            InlineKeyboardButton("🕒 Занятость", callback_data="edit_field:employment_type"),
        ],
        [
            InlineKeyboardButton("📅 Выходные", callback_data="edit_field:ready_for_weekends"),
            InlineKeyboardButton("📝 О себе", callback_data="edit_field:about_me"),
        ],
        [
            InlineKeyboardButton("⭐ Рекомендации", callback_data="edit_field:has_recommendations"),
            InlineKeyboardButton("💬 Связь", callback_data="edit_field:has_whatsapp"),
        ],
        [
            InlineKeyboardButton("📱 Номер", callback_data="edit_field:phone_number"),
        ],
        [InlineKeyboardButton("⬅️ Назад к анкете", callback_data="back_to_summary")],
    ]
    return InlineKeyboardMarkup(keyboard)


def format_telegram_username(username: str | None) -> str:
    """Форматирует Telegram username для отображения."""
    if not username:
        return "Не указан"
    return f"@{username.lstrip('@')}"


def get_contact_method_label(data: dict) -> str:
    """Читабельная подпись выбранного способа связи."""
    return "WhatsApp" if data.get("has_whatsapp") else "Обычный номер"


def get_yes_no_label(value: bool | None) -> str:
    """Преобразует bool в Да/Нет."""
    if value is None:
        return "Не указано"
    return "Да" if value else "Нет"


def get_photo_label(photo_file_id: str | None) -> str:
    """Показывает, загружено ли фото."""
    return "Загружено ✅" if photo_file_id else "Не загружено"


def normalize_phone_number(text: str) -> str | None:
    """Приводит телефон к безопасному формату хранения."""
    raw = text.strip()
    digits = "".join(char for char in raw if char.isdigit())
    if len(digits) < 10 or len(digits) > 15:
        return None

    if raw.startswith("+") or digits.startswith("996"):
        return f"+{digits}"

    return digits


def build_summary(data: dict) -> str:
    """Собирает текстовое резюме анкеты."""
    return (
        "📋 <b>Ваша анкета</b>\n\n"
        f"👤 Имя: {escape(str(data.get('full_name', 'Не указано')))}\n"
        f"🎂 Возраст: {escape(str(data.get('age', 'Не указано')))}\n"
        f"⚧ Пол: {escape(str(data.get('gender', 'Не указано')))}\n"
        f"📷 Фото: {escape(get_photo_label(data.get('photo_file_id')))}\n"
        f"🧰 Профессия: {escape(str(data.get('specializations', 'Не указано')))}\n"
        f"💼 Где работали: {escape(str(data.get('experience', 'Не указано')))}\n"
        f"📍 Районы: {escape(str(data.get('district', 'Не указано')))}\n"
        f"🕒 Занятость: {escape(str(data.get('employment_type', 'Не указано')))}\n"
        f"📅 Готов(а) к выходным: {escape(get_yes_no_label(data.get('ready_for_weekends')))}\n"
        f"📝 О себе: {escape(str(data.get('about_me', 'Не указано')))}\n"
        f"⭐ Есть рекомендации: {escape(get_yes_no_label(data.get('has_recommendations')))}\n"
        f"🔗 Telegram username: {escape(format_telegram_username(data.get('telegram_username')))}\n"
        f"💬 Способ связи: {escape(get_contact_method_label(data))}\n"
        f"📱 Номер: {escape(str(data.get('phone_number', 'Не указан')))}\n\n"
        "Проверьте данные перед отправкой."
    )


async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, *, edit_message: bool = False) -> None:
    """Показывает итоговую анкету с кнопками действий."""
    summary = build_summary(context.user_data)

    if edit_message and update.callback_query:
        await update.callback_query.edit_message_text(
            summary,
            reply_markup=build_confirmation_keyboard(),
            parse_mode="HTML",
        )
        return

    await update.effective_message.reply_text(
        summary,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )
    await update.effective_message.reply_text(
        "Выберите действие:",
        reply_markup=build_confirmation_keyboard(),
    )


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало регистрации."""
    query = update.callback_query
    await query.answer()

    existing = get_employee_by_telegram_id(query.from_user.id)
    if existing:
        await query.edit_message_text(
            "✅ Вы уже зарегистрированы!\n"
            "Используйте /profile для просмотра профиля\n"
            "или /update, чтобы удалить анкету и пройти регистрацию заново."
        )
        return ConversationHandler.END

    context.user_data.clear()
    context.user_data["telegram_username"] = query.from_user.username

    await query.edit_message_text(
        "📝 *Регистрация в Opus*\n\n"
        "Давайте заполним вашу анкету.\n"
        "Вы можете отменить регистрацию в любой момент командой /cancel\n\n"
        "Шаг 1/12: Как вас зовут?",
        parse_mode="Markdown",
    )
    return FULL_NAME


async def full_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем имя."""
    full_name = update.message.text.strip()

    if len(full_name) < 2:
        await update.message.reply_text("⚠️ Введите корректное имя:")
        return FULL_NAME

    context.user_data["full_name"] = full_name

    if context.user_data.get("edit_field") == "full_name":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 2/12: Сколько вам лет? Введите число:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return AGE


async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем возраст."""
    text = update.message.text.strip()

    if not text.isdigit() or int(text) < 14 or int(text) > 100:
        await update.message.reply_text("⚠️ Пожалуйста, введите корректный возраст (число от 14 до 100):")
        return AGE

    context.user_data["age"] = int(text)

    if context.user_data.get("edit_field") == "age":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 3/12: Выберите ваш пол:",
        reply_markup=build_reply_keyboard(GENDER_OPTIONS),
    )
    return GENDER


async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем пол из фиксированного списка."""
    gender = update.message.text.strip()

    if gender not in GENDER_OPTIONS:
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите пол кнопкой ниже:",
            reply_markup=build_reply_keyboard(GENDER_OPTIONS),
        )
        return GENDER

    context.user_data["gender"] = gender

    if context.user_data.get("edit_field") == "gender":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 4/12: Сфотографируйтесь для анкеты, чтобы было четко видно ваше лицо (можно сделать обычное селфи прямо сейчас):",
    )
    return PHOTO


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем фото сотрудника."""
    photos = update.message.photo or []

    if not photos:
        await update.message.reply_text("⚠️ Пожалуйста, отправьте фото именно как изображение.")
        return PHOTO

    context.user_data["photo_file_id"] = photos[-1].file_id

    if context.user_data.get("edit_field") == "photo_file_id":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 5/12: Кем хотите работать? Выберите вариант:",
        reply_markup=build_reply_keyboard(SPECIALIZATION_OPTIONS),
    )
    return SPECIALIZATIONS


async def photo_required_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подсказывает отправить фото, если прислали текст/не фото."""
    await update.message.reply_text("⚠️ Нужно отправить фото. Можно обычное селфи.")
    return PHOTO


async def specializations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем профессию из фиксированного списка."""
    specialization = update.message.text.strip()

    if specialization not in SPECIALIZATION_OPTIONS:
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите профессию кнопкой ниже:",
            reply_markup=build_reply_keyboard(SPECIALIZATION_OPTIONS),
        )
        return SPECIALIZATIONS

    context.user_data["specializations"] = specialization

    if context.user_data.get("edit_field") == "specializations":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 6/12: Где работали раньше? Напишите название заведения и сколько там работали:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return EXPERIENCE


async def experience_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем опыт работы."""
    experience = update.message.text.strip()

    if len(experience) < 5:
        await update.message.reply_text("⚠️ Напишите чуть подробнее: заведение + срок работы.")
        return EXPERIENCE

    context.user_data["experience"] = experience

    if context.user_data.get("edit_field") == "experience":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 7/12: В каких районах готовы работать? Выберите район:",
        reply_markup=build_reply_keyboard(DISTRICT_OPTIONS),
    )
    return DISTRICT


async def district_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем район из фиксированного списка."""
    district = update.message.text.strip()

    if district not in DISTRICT_OPTIONS:
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите район кнопкой ниже:",
            reply_markup=build_reply_keyboard(DISTRICT_OPTIONS),
        )
        return DISTRICT

    context.user_data["district"] = district

    if context.user_data.get("edit_field") == "district":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 8/12: Выберите формат занятости:",
        reply_markup=build_reply_keyboard(EMPLOYMENT_TYPE_OPTIONS),
    )
    return EMPLOYMENT_TYPE


async def employment_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем формат занятости."""
    employment_type = update.message.text.strip()

    if employment_type not in EMPLOYMENT_TYPE_OPTIONS:
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите формат занятости кнопкой ниже:",
            reply_markup=build_reply_keyboard(EMPLOYMENT_TYPE_OPTIONS),
        )
        return EMPLOYMENT_TYPE

    context.user_data["employment_type"] = employment_type

    if context.user_data.get("edit_field") == "employment_type":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 9/12: Готовы работать в выходные?",
        reply_markup=build_reply_keyboard(YES_NO_OPTIONS),
    )
    return WEEKEND_WORK


async def weekend_work_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем готовность работать в выходные."""
    answer = update.message.text.strip()

    if answer not in YES_NO_OPTIONS:
        await update.message.reply_text(
            "⚠️ Выберите «Да» или «Нет» кнопкой ниже:",
            reply_markup=build_reply_keyboard(YES_NO_OPTIONS),
        )
        return WEEKEND_WORK

    context.user_data["ready_for_weekends"] = answer == "Да"

    if context.user_data.get("edit_field") == "ready_for_weekends":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 10/12: Напишите 2-3 предложения о себе:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ABOUT_ME


async def about_me_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем краткий текст о сотруднике."""
    about_me = update.message.text.strip()

    if len(about_me) < 20:
        await update.message.reply_text("⚠️ Напишите чуть подробнее (желательно 2-3 предложения).")
        return ABOUT_ME

    context.user_data["about_me"] = about_me

    if context.user_data.get("edit_field") == "about_me":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 11/12: Есть рекомендации от прошлых работодателей?",
        reply_markup=build_reply_keyboard(YES_NO_OPTIONS),
    )
    return HAS_RECOMMENDATIONS


async def recommendations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем наличие рекомендаций."""
    answer = update.message.text.strip()

    if answer not in YES_NO_OPTIONS:
        await update.message.reply_text(
            "⚠️ Выберите «Да» или «Нет» кнопкой ниже:",
            reply_markup=build_reply_keyboard(YES_NO_OPTIONS),
        )
        return HAS_RECOMMENDATIONS

    context.user_data["has_recommendations"] = answer == "Да"

    if context.user_data.get("edit_field") == "has_recommendations":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 12/12: Выберите способ связи по номеру:",
        reply_markup=build_reply_keyboard(CONTACT_METHOD_OPTIONS),
    )
    return CONTACT_METHOD


async def contact_method_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем способ связи по телефону."""
    method = update.message.text.strip()

    if method not in CONTACT_METHOD_OPTIONS:
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите способ связи кнопкой ниже:",
            reply_markup=build_reply_keyboard(CONTACT_METHOD_OPTIONS),
        )
        return CONTACT_METHOD

    context.user_data["has_whatsapp"] = method == "WhatsApp"

    if context.user_data.get("edit_field") == "has_whatsapp":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 12/12 (последний): Введите номер "
        f"{'для WhatsApp' if context.user_data['has_whatsapp'] else 'телефона'} "
        "в международном формате, например: +996700123456",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PHONE_NUMBER


async def phone_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем номер телефона / WhatsApp."""
    phone_number = normalize_phone_number(update.message.text)

    if not phone_number:
        await update.message.reply_text(
            "⚠️ Введите корректный номер в международном формате, например: +996700123456"
        )
        return PHONE_NUMBER

    context.user_data["phone_number"] = phone_number

    if context.user_data.get("edit_field") == "phone_number":
        context.user_data.pop("edit_field", None)

    await show_confirmation(update, context)
    return CONFIRM


async def edit_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показывает меню редактирования анкеты перед отправкой."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✏️ Что хотите изменить в анкете?",
        reply_markup=build_edit_keyboard(),
    )
    return CONFIRM


async def edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Открывает редактирование выбранного поля."""
    query = update.callback_query
    await query.answer()

    field = query.data.split(":", maxsplit=1)[1]
    context.user_data["edit_field"] = field
    field_label = FIELD_LABELS.get(field, "поле")

    await query.edit_message_text(f"✏️ Редактируем поле: {field_label}")

    if field == "full_name":
        await query.message.reply_text(
            "Введите новое имя:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return FULL_NAME

    if field == "age":
        await query.message.reply_text(
            "Введите новый возраст (число):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return AGE

    if field == "gender":
        await query.message.reply_text(
            "Выберите новый пол:",
            reply_markup=build_reply_keyboard(GENDER_OPTIONS),
        )
        return GENDER

    if field == "photo_file_id":
        await query.message.reply_text(
            "Пришлите новое фото:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return PHOTO

    if field == "specializations":
        await query.message.reply_text(
            "Выберите новую профессию:",
            reply_markup=build_reply_keyboard(SPECIALIZATION_OPTIONS),
        )
        return SPECIALIZATIONS

    if field == "experience":
        await query.message.reply_text(
            "Напишите новый опыт (заведение + срок):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return EXPERIENCE

    if field == "district":
        await query.message.reply_text(
            "Выберите новый район:",
            reply_markup=build_reply_keyboard(DISTRICT_OPTIONS),
        )
        return DISTRICT

    if field == "employment_type":
        await query.message.reply_text(
            "Выберите новый формат занятости:",
            reply_markup=build_reply_keyboard(EMPLOYMENT_TYPE_OPTIONS),
        )
        return EMPLOYMENT_TYPE

    if field == "ready_for_weekends":
        await query.message.reply_text(
            "Готовы работать в выходные?",
            reply_markup=build_reply_keyboard(YES_NO_OPTIONS),
        )
        return WEEKEND_WORK

    if field == "about_me":
        await query.message.reply_text(
            "Напишите обновлённый текст о себе (2-3 предложения):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ABOUT_ME

    if field == "has_recommendations":
        await query.message.reply_text(
            "Есть рекомендации от прошлых работодателей?",
            reply_markup=build_reply_keyboard(YES_NO_OPTIONS),
        )
        return HAS_RECOMMENDATIONS

    if field == "has_whatsapp":
        await query.message.reply_text(
            "Выберите новый способ связи:",
            reply_markup=build_reply_keyboard(CONTACT_METHOD_OPTIONS),
        )
        return CONTACT_METHOD

    await query.message.reply_text(
        "Введите новый номер телефона в международном формате, например: +996700123456",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PHONE_NUMBER


async def back_to_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возвращает пользователя к итоговой анкете."""
    query = update.callback_query
    await query.answer()
    await show_confirmation(update, context, edit_message=True)
    return CONFIRM


async def confirm_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подтверждение и сохранение анкеты."""
    query = update.callback_query
    await query.answer()

    context.user_data["telegram_username"] = query.from_user.username

    data = context.user_data
    employee_data = {
        "telegram_id": query.from_user.id,
        "telegram_username": data.get("telegram_username"),
        "full_name": data["full_name"],
        "age": data["age"],
        "gender": data["gender"],
        "photo_file_id": data.get("photo_file_id"),
        "specializations": data["specializations"],
        "experience": data["experience"],
        "district": data["district"],
        "employment_type": data["employment_type"],
        "ready_for_weekends": data["ready_for_weekends"],
        "about_me": data["about_me"],
        "has_recommendations": data["has_recommendations"],
        "phone_number": data["phone_number"],
        "has_whatsapp": data["has_whatsapp"],
        "is_verified": False,
    }

    try:
        # Скачиваем фото из Telegram и сохраняем в Railway
        if data.get("photo_file_id"):
            from photo_storage import save_photo
            
            # Получаем файл из серверов Telegram
            file = await context.bot.get_file(data["photo_file_id"])
            photo_bytes = await file.download_as_bytearray()
            
            # Сохраняем в Railway PostgreSQL
            save_photo(query.from_user.id, photo_bytes)
            
        # Сохраняем остальные данные в Supabase
        save_employee(employee_data)
        
        await query.edit_message_text(
            "✅ *Анкета отправлена!*\n\n"
            "Ваш профиль успешно сохранён.\n"
            "Если захотите что-то поменять после отправки,\n"
            "используйте /update: бот удалит анкету и вы сможете пройти всё заново.\n\n"
            "Команды:\n"
            "/profile — посмотреть профиль\n"
            "/update — удалить анкету и заполнить заново",
            parse_mode="Markdown",
        )
    except Exception as error:
        error_text = str(error)
        if "PGRST204" in error_text:
            await query.edit_message_text(
                "❌ База данных ещё не обновлена под новую анкету.\n"
                "Нужно применить миграцию `supabase/migrations/007_add_employee_registration_fields.sql`\n"
                "в SQL Editor Supabase и повторить отправку."
            )
            context.user_data.clear()
            return ConversationHandler.END

        await query.edit_message_text(
            f"❌ Ошибка при сохранении: {error_text}\n"
            "Попробуйте позже или обратитесь в поддержку."
        )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена регистрации через inline-кнопку."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Регистрация отменена. Начните заново командой /start")
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена регистрации через команду /cancel."""
    await update.message.reply_text(
        "❌ Регистрация отменена.\nНачните заново командой /start",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


def get_registration_handler() -> ConversationHandler:
    """Возвращает ConversationHandler для регистрации."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_registration, pattern="^start_registration$"),
        ],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name_handler)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age_handler)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_handler)],
            PHOTO: [
                MessageHandler(filters.PHOTO, photo_handler),
                MessageHandler(filters.ALL & ~filters.COMMAND, photo_required_handler),
            ],
            SPECIALIZATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, specializations_handler)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience_handler)],
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, district_handler)],
            EMPLOYMENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, employment_type_handler)],
            WEEKEND_WORK: [MessageHandler(filters.TEXT & ~filters.COMMAND, weekend_work_handler)],
            ABOUT_ME: [MessageHandler(filters.TEXT & ~filters.COMMAND, about_me_handler)],
            HAS_RECOMMENDATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, recommendations_handler)],
            CONTACT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_method_handler)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number_handler)],
            CONFIRM: [
                CallbackQueryHandler(confirm_registration, pattern="^confirm_registration$"),
                CallbackQueryHandler(edit_registration, pattern="^edit_registration$"),
                CallbackQueryHandler(edit_field, pattern="^edit_field:"),
                CallbackQueryHandler(back_to_summary, pattern="^back_to_summary$"),
                CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
        ],
    )
