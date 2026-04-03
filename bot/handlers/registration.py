import asyncio
from html import escape
import logging

logger = logging.getLogger(__name__)

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

from database import get_bot_user_settings, get_employee_by_telegram_id, save_employee
from i18n import (
    get_display_options,
    language_name,
    localize_choice,
    localize_csv_choices,
    parse_choice_value,
    resolve_language,
    tr,
)

# Состояния диалога
(
    FULL_NAME,
    AGE,
    GENDER,
    PHOTO,
    SPECIALIZATIONS,
    EXPERIENCE,
    DISTRICT,
    DISTRICT_CUSTOM,
    EMPLOYMENT_TYPE,
    WEEKEND_WORK,
    SANITARY_BOOK,
    ABOUT_ME,
    CONTACT_METHOD,
    PHONE_NUMBER,
    CONFIRM,
) = range(15)

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


def get_current_language(update: Update | None, context: ContextTypes.DEFAULT_TYPE) -> str:
    context_language = context.user_data.get("bot_language")
    if context_language:
        return resolve_language(context_language=context_language)

    telegram_language = None
    stored_language = None
    if update and update.effective_user:
        telegram_language = update.effective_user.language_code
        user_settings = get_bot_user_settings(update.effective_user.id)
        if user_settings:
            stored_language = user_settings.get("preferred_language")
    language = resolve_language(
        context_language=context.user_data.get("bot_language"),
        stored_language=stored_language,
        telegram_language=telegram_language,
    )
    context.user_data["bot_language"] = language
    return language


async def notify_new_employee_background(employee: dict) -> None:
    try:
        from verification_notifier import notify_new_employee

        logger.info("Отправляем анкету на верификацию для employee_id=%s", employee.get("id"))
        delivered = await notify_new_employee(employee)
        if delivered:
            logger.info("Уведомление о новой анкете доставлено")
        else:
            logger.warning("Уведомление о новой анкете не было доставлено")
    except Exception:
        logger.exception("Ошибка при отправке уведомления верификатору")


def build_reply_keyboard(
    options: list[str],
    columns: int = 2,
    *,
    allow_skip: bool = False,
    language: str = "ru",
    category: str | None = None,
) -> ReplyKeyboardMarkup:
    """Строит клавиатуру выбора с кнопками."""
    display_options = get_display_options(language, category, options) if category else options
    rows = [display_options[index:index + columns] for index in range(0, len(display_options), columns)]
    if allow_skip:
        rows.append([tr(language, "skip")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)

def build_multiselect_inline_keyboard(
    options: list[str],
    selected: set[str],
    prefix: str,
    columns: int = 2,
    add_custom_button: bool = False,
    allow_skip: bool = False,
    language: str = "ru",
    category: str | None = None,
) -> InlineKeyboardMarkup:
    """Строит Inline-клавиатуру для множественного выбора с галочками."""
    keyboard = []
    
    # Разбиваем опции на строки по columns штук
    for index in range(0, len(options), columns):
        row = []
        for opt in options[index:index + columns]:
            display_opt = localize_choice(language, category, opt) if category else opt
            label = display_opt or opt
            text = f"✅ {label}" if opt in selected else label
            callback_data = f"{prefix}_toggle:{opt}"
            row.append(InlineKeyboardButton(text, callback_data=callback_data))
        keyboard.append(row)
    
    done_text = (
        f"▶️ Далее ({len(selected)})"
        if selected
        else ("▶️ Пропустить" if allow_skip else "▶️ Далее")
    )
    keyboard.append([InlineKeyboardButton(done_text, callback_data=f"{prefix}_done")])

    if add_custom_button:
        keyboard.append([InlineKeyboardButton("✍️ Указать свой район" if language == "ru" else "✍️ Өз районуңузду жазыңыз", callback_data=f"{prefix}_custom")])
        
    return InlineKeyboardMarkup(keyboard)


def is_skip_input(text: str | None) -> bool:
    if not text:
        return False
    normalized = text.strip().lower()
    return normalized in {
        tr("ru", "skip").lower(),
        tr("ky", "skip").lower(),
        "skip",
        "⏭ пропустить",
    }


def derive_ready_for_weekends(schedule: str | None) -> bool | None:
    if not schedule:
        return None

    normalized = schedule.strip().lower()
    if "выход" in normalized:
        return True
    if "будни" in normalized:
        return False
    return None


def build_confirmation_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура подтверждения анкеты."""
    keyboard = [
        [InlineKeyboardButton("✅ Отправить анкету" if language == "ru" else "✅ Анкетаны жөнөтүү", callback_data="confirm_registration")],
        [InlineKeyboardButton("✏️ Редактировать" if language == "ru" else "✏️ Өзгөртүү", callback_data="edit_registration")],
        [InlineKeyboardButton("❌ Отменить" if language == "ru" else "❌ Токтотуу", callback_data="cancel_registration")],
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


def build_summary(data: dict, language: str) -> str:
    """Собирает текстовое резюме анкеты."""
    return (
        f"📋 <b>{'Ваша анкета' if language == 'ru' else 'Сиздин анкета'}</b>\n\n"
        f"👤 Имя: {escape(str(data.get('full_name', 'Не указано')))}\n"
        f"🎂 Возраст: {escape(str(data.get('age', 'Не указано')))}\n"
        f"⚧ Пол: {escape(localize_choice(language, 'gender', data.get('gender')) or str(data.get('gender', 'Не указано')))}\n"
        f"📷 Фото: {escape(get_photo_label(data.get('photo_file_id')))}\n"
        f"🧰 Профессия: {escape(localize_csv_choices(language, 'specializations', data.get('specializations')) or str(data.get('specializations', 'Не указано')))}\n"
        f"💼 Опыт работы: {escape(localize_choice(language, 'experience', data.get('experience')) or str(data.get('experience', 'Не указано')))}\n"
        f"📍 Районы: {escape(str(data.get('district', 'Не указано')))}\n"
        f"🕒 Формат работы: {escape(localize_csv_choices(language, 'employment_type', data.get('employment_type')) or str(data.get('employment_type', 'Не указано')))}\n"
        f"📅 График работы: {escape(localize_choice(language, 'schedule', data.get('schedule')) or str(data.get('schedule', 'Не указано')))}\n"
        f"🩺 Сан. книжка: {escape(localize_choice(language, 'sanitary_book', data.get('has_sanitary_book')) or str(data.get('has_sanitary_book', 'Не указано')))}\n"
        f"📝 О себе: {escape(str(data.get('about_me', 'Не указано')))}\n"
        f"💬 Способ связи: {escape(localize_choice(language, 'contact_method', get_contact_method_label(data)) or get_contact_method_label(data))}\n"
        f"📱 Номер: {escape(str(data.get('phone_number', 'Не указан')))}\n\n"
        f"{'Проверьте данные перед отправкой.' if language == 'ru' else 'Жөнөтүүдөн мурун маалыматты текшериңиз.'}"
    )


async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, *, edit_message: bool = False) -> None:
    """Показывает итоговую анкету с кнопками действий."""
    language = get_current_language(update, context)
    summary = build_summary(context.user_data, language)

    if edit_message and update.callback_query:
        await update.callback_query.edit_message_text(
            summary,
            reply_markup=build_confirmation_keyboard(language),
            parse_mode="HTML",
        )
        return

    await update.effective_message.reply_text(
        summary,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )
    await update.effective_message.reply_text(
        tr(language, "choose_action"),
        reply_markup=build_confirmation_keyboard(language),
    )


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало регистрации."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END
    await query.answer()
    language = get_current_language(update, context)
    context.user_data["bot_language"] = language

    existing = await asyncio.to_thread(get_employee_by_telegram_id, query.from_user.id)
    if existing:
        try:
            await query.edit_message_text(
                tr(language, "start_existing", name=existing["full_name"]),
            )
        except Exception:
            await query.message.reply_text(
                tr(language, "start_existing", name=existing["full_name"]),
            )
        return ConversationHandler.END

    bot_language = context.user_data.get("bot_language")
    context.user_data.clear()
    context.user_data["telegram_username"] = query.from_user.username
    context.user_data["bot_language"] = bot_language or language

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    await query.message.reply_text(
        f"📝 *{tr(language, 'registration_title')}*\n\n"
        f"{tr(language, 'registration_intro')}\n\n"
        f"{'Шаг 1/12: Как вас зовут?' if language == 'ru' else '1/12-кадам: Атыңыз ким?'}",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return FULL_NAME


async def full_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем имя."""
    language = get_current_language(update, context)
    full_name = update.message.text.strip()

    if len(full_name) < 2:
        await update.message.reply_text("⚠️ Введите корректное имя:" if language == "ru" else "⚠️ Атыңызды туура жазыңыз:")
        return FULL_NAME

    context.user_data["full_name"] = full_name

    if context.user_data.get("edit_field") == "full_name":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 2/12: Сколько вам лет? Введите число:" if language == "ru" else "2/12-кадам: Жашыңыз канчада? Сан жазыңыз:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return AGE


async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем возраст."""
    language = get_current_language(update, context)
    text = update.message.text.strip()

    if not text.isdigit() or int(text) < 14 or int(text) > 100:
        await update.message.reply_text(
            "⚠️ Пожалуйста, введите корректный возраст (число от 14 до 100):"
            if language == "ru"
            else "⚠️ Туура жашты жазыңыз (14төн 100гө чейин):"
        )
        return AGE

    context.user_data["age"] = int(text)

    if context.user_data.get("edit_field") == "age":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 3/12: Выберите ваш пол:" if language == "ru" else "3/12-кадам: Жынысыңызды тандаңыз:",
        reply_markup=build_reply_keyboard(GENDER_OPTIONS, language=language, category="gender"),
    )
    return GENDER


async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем пол из фиксированного списка."""
    language = get_current_language(update, context)
    gender = parse_choice_value(language, "gender", update.message.text.strip())

    if gender not in GENDER_OPTIONS:
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите пол кнопкой ниже:" if language == "ru" else "⚠️ Жынысты төмөнкү баскычтардан тандаңыз:",
            reply_markup=build_reply_keyboard(GENDER_OPTIONS, language=language, category="gender"),
        )
        return GENDER

    context.user_data["gender"] = gender

    if context.user_data.get("edit_field") == "gender":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        ("Шаг 4/12: " if language == "ru" else "4/12-кадам: ") + tr(language, "photo_skip_prompt"),
        reply_markup=ReplyKeyboardMarkup([[tr(language, "skip")]], resize_keyboard=True, one_time_keyboard=True),
    )
    return PHOTO


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем фото сотрудника."""
    language = get_current_language(update, context)
    if update.message.text and is_skip_input(update.message.text):
        context.user_data["photo_file_id"] = None
    else:
        photos = update.message.photo or []
        if not photos:
            await update.message.reply_text(
                "⚠️ Пожалуйста, отправьте фото именно как изображение."
                if language == "ru"
                else "⚠️ Сураныч, сүрөттү кадимки сүрөт катары жөнөтүңүз."
            )
            return PHOTO
        context.user_data["photo_file_id"] = photos[-1].file_id

    if context.user_data.get("edit_field") == "photo_file_id":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    from telegram import ReplyKeyboardRemove
    await update.message.reply_text("Отлично! 📸" if language == "ru" else "Жакшы! 📸", reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(
        "Шаг 5/12: Кем хотите работать? Можно выбрать несколько вариантов:" if language == "ru" else "5/12-кадам: Кайсы кызматта иштегиңиз келет? Бир нече вариант тандасаңыз болот:",
        reply_markup=build_multiselect_inline_keyboard(SPECIALIZATION_OPTIONS, set(), "spec", language=language),
    )
    return SPECIALIZATIONS


async def photo_required_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подсказывает отправить фото, если прислали текст/не фото."""
    language = get_current_language(update, context)
    await update.message.reply_text("⚠️ Нужно отправить фото. Сделайте обычное селфи." if language == "ru" else "⚠️ Сүрөт жөнөтүңүз. Жөнөкөй селфи жарайт.")
    return PHOTO


async def specializations_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора профессий."""
    query = update.callback_query
    await query.answer()
    language = get_current_language(update, context)

    spec = query.data.split(":", maxsplit=1)[1]
    selected = context.user_data.setdefault("specializations_set", set())

    if spec in selected:
        selected.remove(spec)
    else:
        selected.add(spec)

    await query.edit_message_reply_markup(
        reply_markup=build_multiselect_inline_keyboard(SPECIALIZATION_OPTIONS, selected, "spec", language=language)
    )
    return SPECIALIZATIONS


async def specializations_done_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершение выбора профессий."""
    query = update.callback_query
    selected = context.user_data.get("specializations_set", set())
    language = get_current_language(update, context)

    await query.answer()
    if not selected:
        await query.answer("⚠️ Выберите хотя бы одну специализацию" if language == "ru" else "⚠️ Жок дегенде бир адистик тандаңыз", show_alert=True)
        return SPECIALIZATIONS
    context.user_data["specializations"] = ", ".join(sorted(selected)) if selected else None
    context.user_data.pop("specializations_set", None)

    if context.user_data.get("edit_field") == "specializations":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context, edit_message=True)
        return CONFIRM

    await query.edit_message_text(
        f"Профессии выбраны: {context.user_data['specializations']}"
        if language == "ru"
        else f"Тандалган адистиктер: {context.user_data['specializations']}"
    )
    
    await query.message.reply_text(
        "Шаг 6/12: Какой у вас опыт работы? Выберите подходящий вариант:" if language == "ru" else "6/12-кадам: Иш тажрыйбаңыз кандай? Ылайыктуусун тандаңыз:",
        reply_markup=build_reply_keyboard(EXPERIENCE_OPTIONS, language=language, category="experience"),
    )
    return EXPERIENCE


async def experience_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем опыт работы из кнопок."""
    language = get_current_language(update, context)
    experience = parse_choice_value(language, "experience", update.message.text.strip())

    if experience not in EXPERIENCE_OPTIONS:
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите опыт работы кнопкой ниже:" if language == "ru" else "⚠️ Иш тажрыйбаны төмөнкү баскычтардан тандаңыз:",
            reply_markup=build_reply_keyboard(EXPERIENCE_OPTIONS, language=language, category="experience"),
        )
        return EXPERIENCE

    context.user_data["experience"] = experience

    if context.user_data.get("edit_field") == "experience":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    from telegram import ReplyKeyboardRemove
    await update.message.reply_text("Принято.", reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(
        "Шаг 7/12: В каких районах готовы работать? Можно выбрать несколько или добавить свой район:" if language == "ru" else "7/12-кадам: Кайсы райондордо иштөөгө даярсыз? Бир нече вариантты тандап же өз районуңузду кошо аласыз:",
        reply_markup=build_multiselect_inline_keyboard(DISTRICT_OPTIONS, set(), "dist", add_custom_button=True, language=language),
    )
    return DISTRICT


async def district_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора районов."""
    query = update.callback_query
    await query.answer()
    language = get_current_language(update, context)

    dist = query.data.split(":", maxsplit=1)[1]
    selected = context.user_data.setdefault("district_set", set())

    if dist in selected:
        selected.remove(dist)
    else:
        selected.add(dist)

    await query.edit_message_reply_markup(
        reply_markup=build_multiselect_inline_keyboard(DISTRICT_OPTIONS, selected, "dist", add_custom_button=True, language=language)
    )
    return DISTRICT


async def district_custom_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запрашивает пользовательский район, если его нет в списке."""
    query = update.callback_query
    await query.answer()
    language = get_current_language(update, context)
    await query.message.reply_text(
        "✍️ Напишите свой район одним сообщением.\nЕсли передумали, напишите: Назад"
        if language == "ru"
        else f"✍️ Өз районуңузду бир билдирүү менен жазыңыз.\nЭгер оюңуз өзгөрсө, {tr(language, 'back')} деп жазыңыз",
        reply_markup=ReplyKeyboardRemove(),
    )
    return DISTRICT_CUSTOM


async def district_custom_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Принимает пользовательский район и возвращает к выбору районов."""
    language = get_current_language(update, context)
    custom_district = update.message.text.strip()

    if custom_district.lower() in {"назад", tr(language, "back").lower()}:
        await update.message.reply_text(
            "Продолжаем выбор районов:" if language == "ru" else "Райондорду тандоону улантабыз:",
            reply_markup=build_multiselect_inline_keyboard(
                DISTRICT_OPTIONS,
                context.user_data.setdefault("district_set", set()),
                "dist",
                add_custom_button=True,
                language=language,
            ),
        )
        return DISTRICT

    if len(custom_district) < 2:
        await update.message.reply_text("⚠️ Укажите район хотя бы из 2 символов." if language == "ru" else "⚠️ Районду жок дегенде 2 белгиден жазыңыз.")
        return DISTRICT_CUSTOM

    selected = context.user_data.setdefault("district_set", set())
    selected.add(custom_district)

    await update.message.reply_text(
        (
            f"✅ Добавлен район: {custom_district}\nМожно выбрать ещё районы или нажать «Далее»."
            if language == "ru"
            else f"✅ Район кошулду: {custom_district}\nДагы район тандасаңыз же «Далее» бассаңыз болот."
        ),
        reply_markup=build_multiselect_inline_keyboard(
            DISTRICT_OPTIONS,
            selected,
            "dist",
            add_custom_button=True,
            language=language,
        ),
    )
    return DISTRICT


async def district_done_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершение выбора районов."""
    query = update.callback_query
    selected = context.user_data.get("district_set", set())
    language = get_current_language(update, context)

    await query.answer()
    if not selected:
        await query.answer("⚠️ Выберите хотя бы один район" if language == "ru" else "⚠️ Жок дегенде бир район тандаңыз", show_alert=True)
        return DISTRICT
    context.user_data["district"] = ", ".join(sorted(selected)) if selected else None
    context.user_data.pop("district_set", None)

    if context.user_data.get("edit_field") == "district":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context, edit_message=True)
        return CONFIRM

    await query.edit_message_text(
        f"Районы выбраны: {context.user_data['district']}"
        if language == "ru"
        else f"Тандалган райондор: {context.user_data['district']}"
    )


    await query.message.reply_text(
        "Шаг 8/12: Выберите формат работы (можно несколько):" if language == "ru" else "8/12-кадам: Иш форматын тандаңыз (бир нече вариант болот):",
        reply_markup=build_multiselect_inline_keyboard(EMPLOYMENT_TYPE_OPTIONS, set(), "emp", language=language, category="employment_type"),
    )
    return EMPLOYMENT_TYPE


async def employment_type_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора формата работы."""
    query = update.callback_query
    await query.answer()
    language = get_current_language(update, context)

    emp = query.data.split(":", maxsplit=1)[1]
    selected = context.user_data.setdefault("employment_type_set", set())

    if emp in selected:
        selected.remove(emp)
    else:
        selected.add(emp)

    await query.edit_message_reply_markup(
        reply_markup=build_multiselect_inline_keyboard(EMPLOYMENT_TYPE_OPTIONS, selected, "emp", language=language, category="employment_type")
    )
    return EMPLOYMENT_TYPE


async def employment_type_done_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершение выбора формата занятости."""
    query = update.callback_query
    selected = context.user_data.get("employment_type_set", set())
    language = get_current_language(update, context)

    await query.answer()
    if not selected:
        await query.answer("⚠️ Выберите хотя бы один формат работы" if language == "ru" else "⚠️ Жок дегенде бир иш форматын тандаңыз", show_alert=True)
        return EMPLOYMENT_TYPE
    context.user_data["employment_type"] = ", ".join(sorted(selected)) if selected else None
    context.user_data.pop("employment_type_set", None)

    if context.user_data.get("edit_field") == "employment_type":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context, edit_message=True)
        return CONFIRM

    await query.edit_message_text(
        f"Формат работы: {localize_csv_choices(language, 'employment_type', context.user_data['employment_type'])}"
        if language == "ru"
        else f"Иш форматы: {localize_csv_choices(language, 'employment_type', context.user_data['employment_type'])}"
    )

    await query.message.reply_text(
        "Шаг 9/12: Выберите график работы:" if language == "ru" else "9/12-кадам: Иш графигин тандаңыз:",
        reply_markup=build_reply_keyboard(SCHEDULE_OPTIONS, language=language, category="schedule"),
    )
    return WEEKEND_WORK


async def schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем график работы."""
    language = get_current_language(update, context)
    answer = parse_choice_value(language, "schedule", update.message.text.strip())

    if answer not in SCHEDULE_OPTIONS:
        await update.message.reply_text(
            "⚠️ Выберите график работы кнопкой ниже:" if language == "ru" else "⚠️ Иш графигин төмөнкү баскычтардан тандаңыз:",
            reply_markup=build_reply_keyboard(SCHEDULE_OPTIONS, language=language, category="schedule"),
        )
        return WEEKEND_WORK

    context.user_data["schedule"] = answer

    if context.user_data.get("edit_field") == "schedule":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 10/12: Санитарная книжка?" if language == "ru" else "10/12-кадам: Санитардык китепче барбы?",
        reply_markup=build_reply_keyboard(SANITARY_BOOK_OPTIONS, language=language, category="sanitary_book"),
    )
    return SANITARY_BOOK



async def sanitary_book_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = get_current_language(update, context)
    answer = parse_choice_value(language, "sanitary_book", update.message.text.strip())
    if answer not in SANITARY_BOOK_OPTIONS:
        await update.message.reply_text(
            "⚠️ Выберите вариант кнопкой ниже:" if language == "ru" else "⚠️ Вариантты төмөнкү баскычтардан тандаңыз:",
            reply_markup=build_reply_keyboard(SANITARY_BOOK_OPTIONS, language=language, category="sanitary_book")
        )
        return SANITARY_BOOK
        
    context.user_data["has_sanitary_book"] = answer
    if context.user_data.get("edit_field") == "has_sanitary_book":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM
        
    await update.message.reply_text(
        tr(language, "about_prompt"),
        reply_markup=ReplyKeyboardMarkup([[tr(language, "skip")]], resize_keyboard=True, one_time_keyboard=True),
    )
    return ABOUT_ME


async def about_me_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем краткий текст о сотруднике."""
    language = get_current_language(update, context)
    about_me = update.message.text.strip()

    if is_skip_input(about_me):
        context.user_data["about_me"] = None
    elif len(about_me) < 10:
        await update.message.reply_text("⚠️ Напишите хотя бы 1 короткое предложение или нажмите «Пропустить»." if language == "ru" else "⚠️ Жок дегенде 1 кыска сүйлөм жазыңыз же өткөрүп жибериңиз.")
        return ABOUT_ME
    else:
        context.user_data["about_me"] = about_me

    if context.user_data.get("edit_field") == "about_me":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        "Шаг 12/12: Выберите способ связи по номеру:" if language == "ru" else "12/12-кадам: Номер аркылуу байланыш түрүн тандаңыз:",
        reply_markup=build_reply_keyboard(CONTACT_METHOD_OPTIONS, language=language, category="contact_method"),
    )
    return CONTACT_METHOD




async def contact_method_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем способ связи по телефону."""
    language = get_current_language(update, context)
    method = parse_choice_value(language, "contact_method", update.message.text.strip())

    if method not in CONTACT_METHOD_OPTIONS:
        await update.message.reply_text(
            "⚠️ Пожалуйста, выберите способ связи кнопкой ниже:" if language == "ru" else "⚠️ Байланыш түрүн төмөнкү баскычтардан тандаңыз:",
            reply_markup=build_reply_keyboard(CONTACT_METHOD_OPTIONS, language=language, category="contact_method"),
        )
        return CONTACT_METHOD

    context.user_data["has_whatsapp"] = (method == "WhatsApp")

    if context.user_data.get("edit_field") == "has_whatsapp":
        context.user_data.pop("edit_field", None)
        await show_confirmation(update, context)
        return CONFIRM

    await update.message.reply_text(
        (
            "Шаг 12/12 (последний): Введите номер "
            f"{'для WhatsApp' if context.user_data['has_whatsapp'] else 'телефона'} "
            "в международном формате, например: +996700123456"
        ) if language == "ru" else (
            "12/12-кадам (акыркы): "
            f"{'WhatsApp үчүн' if context.user_data['has_whatsapp'] else 'телефон'} "
            "номерди эл аралык форматта жазыңыз, мисалы: +996700123456"
        ),
        reply_markup=ReplyKeyboardRemove(),
    )
    return PHONE_NUMBER


async def phone_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем номер телефона / WhatsApp."""
    language = get_current_language(update, context)
    phone_number = normalize_phone_number(update.message.text)

    if not phone_number:
        await update.message.reply_text(
            "⚠️ Введите корректный номер в международном формате, например: +996700123456"
            if language == "ru"
            else "⚠️ Номерди эл аралык форматта туура жазыңыз, мисалы: +996700123456"
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
    language = get_current_language(update, context)
    await query.edit_message_text(
        "✏️ Что хотите изменить в анкете?" if language == "ru" else "✏️ Анкетада эмнени өзгөрткүңүз келет?",
        reply_markup=build_edit_keyboard(),
    )
    return CONFIRM


async def edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Открывает редактирование выбранного поля."""
    query = update.callback_query
    await query.answer()
    language = get_current_language(update, context)

    field = query.data.split(":", maxsplit=1)[1]
    context.user_data["edit_field"] = field
    field_label = FIELD_LABELS.get(field, "поле")

    await query.edit_message_text(
        f"✏️ Редактируем поле: {field_label}" if language == "ru" else f"✏️ Талааны өзгөртүү: {field_label}"
    )

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
            reply_markup=build_reply_keyboard(GENDER_OPTIONS, language=language, category="gender"),
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
            reply_markup=build_multiselect_inline_keyboard(SPECIALIZATION_OPTIONS, set(), "spec", language=language),
        )
        return SPECIALIZATIONS

    if field == "experience":
        await query.message.reply_text(
            "Выберите актуальный опыт работы:",
            reply_markup=build_reply_keyboard(EXPERIENCE_OPTIONS, language=language, category="experience"),
        )
        return EXPERIENCE

    if field == "district":
        await query.message.reply_text(
            "Выберите районы для работы (можно несколько) или добавьте свой:",
            reply_markup=build_multiselect_inline_keyboard(DISTRICT_OPTIONS, set(), "dist", add_custom_button=True, language=language),
        )
        return DISTRICT

    if field == "employment_type":
        await query.message.reply_text(
            "Выберите новый формат работы (можно несколько):",
            reply_markup=build_multiselect_inline_keyboard(EMPLOYMENT_TYPE_OPTIONS, set(), "emp", language=language, category="employment_type"),
        )
        return EMPLOYMENT_TYPE

    if field == "schedule":
        await query.message.reply_text(
            "Выберите новый график работы:",
            reply_markup=build_reply_keyboard(SCHEDULE_OPTIONS, language=language, category="schedule"),
        )
        return WEEKEND_WORK


    if field == "has_sanitary_book":
        await query.message.reply_text(
            "Выберите наличие санитарной книжки:",
            reply_markup=build_reply_keyboard(SANITARY_BOOK_OPTIONS, language=language, category="sanitary_book"),
        )
        return SANITARY_BOOK

    if field == "about_me":
        await query.message.reply_text(
            "Напишите обновлённый текст о себе (1-2 предложения) или «Пропустить»:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ABOUT_ME

    if field == "has_whatsapp":
        await query.message.reply_text(
            "Выберите новый способ связи:",
            reply_markup=build_reply_keyboard(CONTACT_METHOD_OPTIONS, language=language, category="contact_method"),
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
    language = get_current_language(update, context)

    context.user_data["telegram_username"] = query.from_user.username

    data = context.user_data
    employee_data = {
        "telegram_id": query.from_user.id,
        "telegram_username": data.get("telegram_username"),
        "full_name": data.get("full_name", "Не указано"),
        "age": data.get("age"),
        "gender": data.get("gender"),
        "photo_file_id": data.get("photo_file_id"),
        "specializations": data.get("specializations"),
        "experience": data.get("experience"),
        "district": data.get("district"),
        "employment_type": data.get("employment_type"),
        "schedule": data.get("schedule"),
        "ready_for_weekends": derive_ready_for_weekends(data.get("schedule")),
        "has_sanitary_book": data.get("has_sanitary_book"),
        "about_me": data.get("about_me"),
        "has_recommendations": None,
        "phone_number": data.get("phone_number"),
        "has_whatsapp": data.get("has_whatsapp"),
        "preferred_language": language,
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
            await asyncio.to_thread(save_photo, query.from_user.id, bytes(photo_bytes))
            
        # Сохраняем остальные данные в Supabase
        saved_employee = await asyncio.to_thread(save_employee, employee_data)
        if not saved_employee or not saved_employee.get("id"):
            saved_employee = await asyncio.to_thread(get_employee_by_telegram_id, query.from_user.id) or employee_data
        
        await query.edit_message_text(
            (
                "✅ *Анкета отправлена!*\n\n"
                "Ваш профиль успешно сохранён.\n"
                "Сейчас анкета отправлена на ручную проверку.\n"
                "Если захотите что-то поменять после отправки,\n"
                "используйте /update: бот удалит анкету и вы сможете пройти всё заново.\n\n"
                "Команды:\n"
                "/profile — посмотреть профиль\n"
                "/update — удалить анкету и заполнить заново"
            ) if language == "ru" else (
                "✅ *Анкета жөнөтүлдү!*\n\n"
                "Профилиңиз ийгиликтүү сакталды.\n"
                "Эми анкета кол менен текшерүүгө жөнөтүлдү.\n"
                "Кийин өзгөртүү керек болсо,\n"
                "/update колдонуңуз: бот анкетаны өчүрүп, кайра толтурууга мүмкүнчүлүк берет.\n\n"
                "Буйруктар:\n"
                "/profile — профилди көрүү\n"
                "/update — өчүрүп кайра толтуруу"
            ),
            parse_mode="Markdown",
        )
        asyncio.create_task(notify_new_employee_background(saved_employee))
    except Exception as error:
        error_text = str(error)
        if "PGRST204" in error_text:
            await query.edit_message_text(
                "❌ База данных ещё не обновлена под новую анкету.\n"
                "Нужно применить миграции: `supabase/migrations/015_add_sanitary_book.sql` и `supabase/migrations/019_add_employee_preferred_language.sql` в SQL Editor Supabase и повторить отправку."
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
    language = get_current_language(update, context)
    await query.edit_message_text(f"❌ {tr(language, 'cancelled')}")
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена регистрации через команду /cancel."""
    language = get_current_language(update, context)
    await update.message.reply_text(
        f"❌ {tr(language, 'cancelled')}",
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
        allow_reentry=True,
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
                CallbackQueryHandler(district_custom_handler, pattern="^dist_custom$"),
                CallbackQueryHandler(district_done_handler, pattern="^dist_done$"),
            ],
            DISTRICT_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, district_custom_input_handler)],
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
