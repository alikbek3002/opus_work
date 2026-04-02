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
    SANITARY_BOOK,
    ABOUT_ME,
    CONTACT_METHOD,
    PHONE_NUMBER,
    CONFIRM,
) = range(14)

CONTACT_METHOD_OPTIONS = ["WhatsApp", "Обычный номер"]
GENDER_OPTIONS = ["Мужчина", "Женщина"]
DISTRICT_OPTIONS = [
    "Бишкек (весь город)",
    "ЦУМ",
    "Бишкек Парк",
    "Филармония",
    "Моссовет",
    "Ош базар",
    "Аламединский рынок",
    "Тунгуч",
    "Микрорайоны",
    "7 мкр",
    "12 мкр",
    "Учкун мкр",
    "Джал",
    "Южный Магистраль",
    "Кызыл-Аскер",
    "Ак-Ордо",
    "Ак-Орго",
    "Ала-Тоо",
    "Дордой",
    "Дордой-1",
    "Аламедин-1",
    "Лебединовка",
    "Кок-Джар",
    "Орто-Сай",
    "Орто-Сай село",
    "Чон-Арык",
    "Нижняя Ала-Арча",
    "Новопавловка",
    "Новопокровка",
    "Пригородное",
    "Военно-Антоновка",
    "Байтик",
]
SPECIALIZATION_OPTIONS = [
    "Официант",
    "Повар универсал",
    "Кухработник",
    "Посудомойщица",
    "Бармен",
    "Продавец-консультант",
    "Кассир",
    "Грузчик",
    "Помощник повара",
    "Клинер",
]
EXPERIENCE_OPTIONS = ["Без опыта", "До 1 года", "1–2 года", "2–5 лет", "5+ лет"]
EMPLOYMENT_TYPE_OPTIONS = ["Подработки", "Сезонная", "Постоянная работа"]
SCHEDULE_OPTIONS = ["Только будни", "Будни + выходные", "Только выходные", "Любые дни"]
SANITARY_BOOK_OPTIONS = ["Есть", "Нет", "Готов(а) сделать"]
YES_NO_OPTIONS = ["Да", "Нет"]
FIELD_LABELS = {
    "full_name": "Имя",
    "age": "Возраст",
    "gender": "Пол",
    "photo_file_id": "Фото",
    "specializations": "Профессии",
    "experience": "Опыт работы",
    "district": "Районы",
    "employment_type": "Формат работы",
    "schedule": "График работы",
    "has_sanitary_book": "Санитарная книжка",
    "about_me": "О себе",
    "has_recommendations": "Рекомендации",
    "has_whatsapp": "Способ связи",
    "phone_number": "Номер телефона",
}


def build_reply_keyboard(options: list[str], columns: int = 2) -> ReplyKeyboardMarkup:
    """Строит клавиатуру выбора с кнопками."""
    rows = [options[index:index + columns] for index in range(0, len(options), columns)]
    return ReplyKeyboardMarkup(rows + [["Пропустить"]], resize_keyboard=True, one_time_keyboard=True)

def build_multiselect_inline_keyboard(options: list[str], selected: set[str], prefix: str, columns: int = 2) -> InlineKeyboardMarkup:
    """Строит Inline-клавиатуру для множественного выбора с галочками."""
    keyboard = []
    
    # Разбиваем опции на строки по columns штук
    for index in range(0, len(options), columns):
        row = []
        for opt in options[index:index + columns]:
            text = f"✅ {opt}" if opt in selected else opt
            callback_data = f"{prefix}_toggle:{opt}"
            row.append(InlineKeyboardButton(text, callback_data=callback_data))
        keyboard.append(row)
    
    # Всегда добавляем кнопку Готово/Пропустить
    done_text = f"▶️ Далее (выбрано: {len(selected)})" if selected else "▶️ Пропустить (не выбрано)"
    keyboard.append([InlineKeyboardButton(done_text, callback_data=f"{prefix}_done")])
        
    return InlineKeyboardMarkup(keyboard)


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
            InlineKeyboardButton("📅 График", callback_data="edit_field:schedule"),
            InlineKeyboardButton("🩺 Сан. книжка", callback_data="edit_field:has_sanitary_book"),
        ],
        [
            InlineKeyboardButton("📝 О себе", callback_data="edit_field:about_me"),
        ],
        [
            InlineKeyboardButton("💬 Связь", callback_data="edit_field:has_whatsapp"),
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
        f"💼 Опыт работы: {escape(str(data.get('experience', 'Не указано')))}\n"
        f"📍 Районы: {escape(str(data.get('district', 'Не указано')))}\n"
        f"🕒 Формат работы: {escape(str(data.get('employment_type', 'Не указано')))}\n"
        f"📅 График работы: {escape(str(data.get('schedule', 'Не указано')))}\n"
        f"🩺 Сан. книжка: {escape(str(data.get('has_sanitary_book', 'Не указано')))}\n"
        f"📝 О себе: {escape(str(data.get('about_me', 'Не указано')))}\n"
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
        reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True, one_time_keyboard=True),
    )
    return AGE


async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем возраст."""
    text = update.message.text.strip()

    if text == "Пропустить":
        context.user_data["age"] = None
    elif not text.isdigit() or int(text) < 14 or int(text) > 100:
        await update.message.reply_text("⚠️ Пожалуйста, введите корректный возраст (число от 14 до 100):")
        return AGE

    if text != "Пропустить":
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

    if gender not in GENDER_OPTIONS and gender != "Пропустить":
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите пол кнопкой ниже:",
            reply_markup=build_reply_keyboard(GENDER_OPTIONS),
        )
        return GENDER

    context.user_data["gender"] = gender if gender != "Пропустить" else None

    if context.user_data.get("edit_field") == "gender":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 4/12: Сделайте фото для анкеты или вставьте из галереи. Анкеты с фото открываются на 70% чаще!",
        reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True, one_time_keyboard=True),
    )
    return PHOTO


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем фото сотрудника."""
    if update.message.text and update.message.text.strip() == "Пропустить":
        context.user_data["photo_file_id"] = None
    else:
        photos = update.message.photo or []
        if not photos:
            await update.message.reply_text("⚠️ Пожалуйста, отправьте фото именно как изображение.")
            return PHOTO
        context.user_data["photo_file_id"] = photos[-1].file_id

    if context.user_data.get("edit_field") == "photo_file_id":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    from telegram import ReplyKeyboardRemove
    await update.message.reply_text("Отлично! 📸", reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(
        "Шаг 5/12: Кем хотите работать? Можно выбрать несколько вариантов:",
        reply_markup=build_multiselect_inline_keyboard(SPECIALIZATION_OPTIONS, set(), "spec"),
    )
    return SPECIALIZATIONS


async def photo_required_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подсказывает отправить фото, если прислали текст/не фото."""
    await update.message.reply_text("⚠️ Нужно отправить фото. Сделайте обычное селфи.")
    return PHOTO


async def specializations_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора профессий."""
    query = update.callback_query
    await query.answer()

    spec = query.data.split(":", maxsplit=1)[1]
    selected = context.user_data.setdefault("specializations_set", set())

    if spec in selected:
        selected.remove(spec)
    else:
        selected.add(spec)

    await query.edit_message_reply_markup(
        reply_markup=build_multiselect_inline_keyboard(SPECIALIZATION_OPTIONS, selected, "spec")
    )
    return SPECIALIZATIONS


async def specializations_done_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершение выбора профессий."""
    query = update.callback_query
    selected = context.user_data.get("specializations_set", set())

    await query.answer()
    context.user_data["specializations"] = ", ".join(sorted(selected)) if selected else None
    context.user_data.pop("specializations_set", None)

    if context.user_data.get("edit_field") == "specializations":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context, edit_message=True)
        return CONFIRM

    await query.edit_message_text(f"Профессии выбраны: {context.user_data['specializations']}")
    
    await query.message.reply_text(
        "Шаг 6/12: Какой у вас опыт работы? Выберите подходящий вариант:",
        reply_markup=build_reply_keyboard(EXPERIENCE_OPTIONS),
    )
    return EXPERIENCE


async def experience_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем опыт работы из кнопок."""
    experience = update.message.text.strip()

    if experience not in EXPERIENCE_OPTIONS and experience != "Пропустить":
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите опыт работы кнопкой ниже:",
            reply_markup=build_reply_keyboard(EXPERIENCE_OPTIONS),
        )
        return EXPERIENCE

    context.user_data["experience"] = experience if experience != "Пропустить" else None

    if context.user_data.get("edit_field") == "experience":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    from telegram import ReplyKeyboardRemove
    await update.message.reply_text("Принято.", reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(
        "Шаг 7/12: В каких районах готовы работать? Можно выбрать несколько:",
        reply_markup=build_multiselect_inline_keyboard(DISTRICT_OPTIONS, set(), "dist"),
    )
    return DISTRICT


async def district_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора районов."""
    query = update.callback_query
    await query.answer()

    dist = query.data.split(":", maxsplit=1)[1]
    selected = context.user_data.setdefault("district_set", set())

    if dist in selected:
        selected.remove(dist)
    else:
        selected.add(dist)

    await query.edit_message_reply_markup(
        reply_markup=build_multiselect_inline_keyboard(DISTRICT_OPTIONS, selected, "dist")
    )
    return DISTRICT


async def district_done_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершение выбора районов."""
    query = update.callback_query
    selected = context.user_data.get("district_set", set())

    await query.answer()
    context.user_data["district"] = ", ".join(sorted(selected)) if selected else None
    context.user_data.pop("district_set", None)

    if context.user_data.get("edit_field") == "district":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context, edit_message=True)
        return CONFIRM

    await query.edit_message_text(f"Районы выбраны: {context.user_data['district']}")


    await query.message.reply_text(
        "Шаг 8/12: Выберите формат работы (можно несколько):",
        reply_markup=build_multiselect_inline_keyboard(EMPLOYMENT_TYPE_OPTIONS, set(), "emp"),
    )
    return EMPLOYMENT_TYPE


async def employment_type_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора формата работы."""
    query = update.callback_query
    await query.answer()

    emp = query.data.split(":", maxsplit=1)[1]
    selected = context.user_data.setdefault("employment_type_set", set())

    if emp in selected:
        selected.remove(emp)
    else:
        selected.add(emp)

    await query.edit_message_reply_markup(
        reply_markup=build_multiselect_inline_keyboard(EMPLOYMENT_TYPE_OPTIONS, selected, "emp")
    )
    return EMPLOYMENT_TYPE


async def employment_type_done_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершение выбора формата занятости."""
    query = update.callback_query
    selected = context.user_data.get("employment_type_set", set())

    await query.answer()
    context.user_data["employment_type"] = ", ".join(sorted(selected)) if selected else None
    context.user_data.pop("employment_type_set", None)

    if context.user_data.get("edit_field") == "employment_type":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context, edit_message=True)
        return CONFIRM

    await query.edit_message_text(f"Формат работы: {context.user_data['employment_type']}")

    await query.message.reply_text(
        "Шаг 9/12: Выберите график работы:",
        reply_markup=build_reply_keyboard(SCHEDULE_OPTIONS),
    )
    return WEEKEND_WORK


async def schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем график работы."""
    answer = update.message.text.strip()

    if answer not in SCHEDULE_OPTIONS and answer != "Пропустить":
        await update.message.reply_text(
            "⚠️ Выберите график работы кнопкой ниже:",
            reply_markup=build_reply_keyboard(SCHEDULE_OPTIONS),
        )
        return WEEKEND_WORK

    context.user_data["schedule"] = answer if answer != "Пропустить" else None

    if context.user_data.get("edit_field") == "schedule":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 10/12: Санитарная книжка?",
        reply_markup=build_reply_keyboard(SANITARY_BOOK_OPTIONS),
    )
    return SANITARY_BOOK



async def sanitary_book_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip()
    if answer not in SANITARY_BOOK_OPTIONS and answer != "Пропустить":
        await update.message.reply_text(
            "⚠️ Выберите вариант кнопкой ниже:", 
            reply_markup=build_reply_keyboard(SANITARY_BOOK_OPTIONS)
        )
        return SANITARY_BOOK
        
    context.user_data["has_sanitary_book"] = answer if answer != "Пропустить" else None
    if context.user_data.get("edit_field") == "has_sanitary_book":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM
        
    await update.message.reply_text(
        "Шаг 11/12: Напишите 2-3 предложения о себе:",
        reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True, one_time_keyboard=True),
    )
    return ABOUT_ME


async def about_me_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем краткий текст о сотруднике."""
    about_me = update.message.text.strip()

    if about_me == "Пропустить":
        context.user_data["about_me"] = None
    elif len(about_me) < 20:
        await update.message.reply_text("⚠️ Напишите чуть подробнее (желательно 2-3 предложения).")
        return ABOUT_ME
    else:
        context.user_data["about_me"] = about_me

    if context.user_data.get("edit_field") == "about_me":
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

    if method not in CONTACT_METHOD_OPTIONS and method != "Пропустить":
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите способ связи кнопкой ниже:",
            reply_markup=build_reply_keyboard(CONTACT_METHOD_OPTIONS),
        )
        return CONTACT_METHOD

    context.user_data["has_whatsapp"] = (method == "WhatsApp") if method != "Пропустить" else None

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
            "Выберите профессии (можно несколько):",
            reply_markup=build_multiselect_inline_keyboard(SPECIALIZATION_OPTIONS, set(), "spec"),
        )
        return SPECIALIZATIONS

    if field == "experience":
        await query.message.reply_text(
            "Выберите актуальный опыт работы:",
            reply_markup=build_reply_keyboard(EXPERIENCE_OPTIONS),
        )
        return EXPERIENCE

    if field == "district":
        await query.message.reply_text(
            "Выберите районы для работы (можно несколько):",
            reply_markup=build_multiselect_inline_keyboard(DISTRICT_OPTIONS, set(), "dist"),
        )
        return DISTRICT

    if field == "employment_type":
        await query.message.reply_text(
            "Выберите новый формат работы (можно несколько):",
            reply_markup=build_multiselect_inline_keyboard(EMPLOYMENT_TYPE_OPTIONS, set(), "emp"),
        )
        return EMPLOYMENT_TYPE

    if field == "schedule":
        await query.message.reply_text(
            "Выберите новый график работы:",
            reply_markup=build_reply_keyboard(SCHEDULE_OPTIONS),
        )
        return WEEKEND_WORK


    if field == "has_sanitary_book":
        await query.message.reply_text(
            "Выберите наличие санитарной книжки:",
            reply_markup=build_reply_keyboard(SANITARY_BOOK_OPTIONS),
        )
        return SANITARY_BOOK

    if field == "about_me":
        await query.message.reply_text(
            "Напишите обновлённый текст о себе (2-3 предложения):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ABOUT_ME

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
        "schedule": data.get("schedule"),
        "has_sanitary_book": data["has_sanitary_book"],
        "about_me": data["about_me"],
        "has_recommendations": None,
        "phone_number": data["phone_number"],
        "has_whatsapp": data["has_whatsapp"],
        "is_verified": False,
        "verification_status": "pending",
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
        saved_employee = save_employee(employee_data)

        from verification_notifier import notify_new_employee
        await notify_new_employee(saved_employee)
        
        await query.edit_message_text(
            "✅ *Анкета отправлена!*\n\n"
            "Ваш профиль успешно сохранён.\n"
            "Сейчас анкета отправлена на ручную проверку.\n"
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
                "Нужно применить миграцию: `supabase/migrations/015_add_sanitary_book.sql` в SQL Editor Supabase и повторить отправку."
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
                MessageHandler((filters.PHOTO | filters.TEXT) & ~filters.COMMAND, photo_handler),
                MessageHandler(filters.ALL & ~filters.COMMAND, photo_required_handler),
            ],
            SPECIALIZATIONS: [
                CallbackQueryHandler(specializations_toggle_handler, pattern="^spec_toggle:"),
                CallbackQueryHandler(specializations_done_handler, pattern="^spec_done$"),
            ],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience_handler)],
            DISTRICT: [
                CallbackQueryHandler(district_toggle_handler, pattern="^dist_toggle:"),
                CallbackQueryHandler(district_done_handler, pattern="^dist_done$"),
            ],
            EMPLOYMENT_TYPE: [
                CallbackQueryHandler(employment_type_toggle_handler, pattern="^emp_toggle:"),
                CallbackQueryHandler(employment_type_done_handler, pattern="^emp_done$"),
            ],
            WEEKEND_WORK: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule_handler)],
            SANITARY_BOOK: [MessageHandler(filters.TEXT & ~filters.COMMAND, sanitary_book_handler)],
            ABOUT_ME: [MessageHandler(filters.TEXT & ~filters.COMMAND, about_me_handler)],
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
