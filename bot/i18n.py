from __future__ import annotations

from typing import Iterable

SUPPORTED_LANGUAGES = ("ru", "ky")
DEFAULT_LANGUAGE = "ru"

LANGUAGE_NAMES = {
    "ru": "Русский",
    "ky": "Кыргызча",
}

TEXTS: dict[str, dict[str, str]] = {
    "start_existing": {
        "ru": "Привет, {name}!\n\nВы уже зарегистрированы в системе OPUS Анкеты.\nИспользуйте /profile, чтобы посмотреть профиль,\nили /update, чтобы удалить анкету и заполнить её заново.",
        "ky": "Саламатсызбы, {name}!\n\nСиз OPUS Анкеталар системасында катталгансыз.\nПрофилди көрүү үчүн /profile колдонуңуз,\nже анкетаны өчүрүп кайра толтуруу үчүн /update басыңыз.",
    },
    "start_intro": {
        "ru": "Здравствуйте, {name}! 👋\n\nДобро пожаловать в OPUS Анкеты.\nВыберите язык и начните регистрацию.",
        "ky": "Саламатсызбы, {name}! 👋\n\nOPUS Анкеталарга кош келиңиз.\nТилди тандап, каттоону баштаңыз.",
    },
    "start_returning": {
        "ru": "Здравствуйте, {name}! 👋\n\nПродолжим. Нажмите кнопку ниже, чтобы заполнить анкету.",
        "ky": "Саламатсызбы, {name}! 👋\n\nУланталы. Анкетаны толтуруу үчүн төмөнкү баскычты басыңыз.",
    },
    "start_registered_intro": {
        "ru": "Здравствуйте, {name}! 👋\n\nВаш профиль уже сохранён. Ниже можно открыть помощь или использовать команды меню.",
        "ky": "Саламатсызбы, {name}! 👋\n\nПрофилиңиз сакталган. Төмөндөн жардамды ачсаңыз болот же менюдагы буйруктарды колдонуңуз.",
    },
    "language_changed": {
        "ru": "Язык бота обновлён: {language_label} ✅",
        "ky": "Боттун тили жаңыртылды: {language_label} ✅",
    },
    "language_choose": {
        "ru": "🌐 Выберите язык бота:",
        "ky": "🌐 Боттун тилин тандаңыз:",
    },
    "help_text": {
        "ru": "OPUS Анкеты поможет заполнить анкету и показать её работодателям.\n\nКоманды:\n/start — главное меню\n/profile — моя анкета\n/update — удалить и заполнить заново\n/language — выбрать язык\n/cancel — отменить регистрацию",
        "ky": "OPUS Анкеталар анкетаңызды толтуруп, иш берүүчүлөргө көрсөтүүгө жардам берет.\n\nБуйруктар:\n/start — негизги меню\n/profile — менин анкетам\n/update — өчүрүп кайра толтуруу\n/language — тил тандоо\n/cancel — каттоону токтотуу",
    },
    "btn_register": {
        "ru": "📝 Зарегистрироваться",
        "ky": "📝 Катталуу",
    },
    "btn_profile": {
        "ru": "Моя анкета",
        "ky": "Менин анкетам",
    },
    "btn_language": {
        "ru": "Язык",
        "ky": "Тил",
    },
    "btn_help": {
        "ru": "❓ Помощь",
        "ky": "❓ Жардам",
    },
    "btn_update": {
        "ru": "Заполнить заново",
        "ky": "Кайра толтуруу",
    },
    "registration_title": {
        "ru": "Регистрация в OPUS Анкеты",
        "ky": "OPUS Анкеталарга катталуу",
    },
    "registration_intro": {
        "ru": "Давайте заполним вашу анкету.\nВы можете отменить регистрацию в любой момент командой /cancel",
        "ky": "Келиңиз, анкетаңызды толтуралы.\nКаттоону каалаган убакта /cancel буйругу менен токтото аласыз",
    },
    "choose_action": {
        "ru": "Выберите действие:",
        "ky": "Аракетти тандаңыз:",
    },
    "cancelled": {
        "ru": "Регистрация отменена.\nНачните заново командой /start",
        "ky": "Каттоо токтотулду.\nКайра баштоо үчүн /start басыңыз",
    },
    "photo_skip_prompt": {
        "ru": "Фото для анкеты (можно пропустить).",
        "ky": "Анкета үчүн сүрөт (өткөрүп жиберсе болот).",
    },
    "about_prompt": {
        "ru": "Шаг 12/13: Напишите коротко о себе:\n\n✍️ Напишите 1-2 предложения о себе.\n\nНапример:\n- Где работали и сколько\n- Ваши сильные стороны\n- Что отличает вас от других\n\nПример: «Работала официанткой 2 года, знаю сервировку.\nВсегда прихожу вовремя и улыбаюсь гостям.»\n\nЭто поле видят работодатели — напишите честно и кратко.\nМожно нажать «Пропустить».",
        "ky": "12/13-кадам: Өзүңүз жөнүндө кыскача жазыңыз:\n\n✍️ Өзүңүз жөнүндө 1-2 сүйлөм жазыңыз.\n\nМисалы:\n- Кайда жана канча иштедиңиз\n- Күчтүү жактарыңыз\n- Сизди башкалардан эмне айырмалайт\n\nМисал: «2 жыл официант болуп иштегем, сервировканы билем.\nАр дайым өз убагында келип, конокторго жылмайып кызмат кылам.»\n\nБул талааны иш берүүчүлөр көрөт — чынчыл жана кыска жазыңыз.\n«Пропустить» бассаңыз болот.",
    },
    "profile_empty": {
        "ru": "Вы ещё не зарегистрированы. Напишите /start",
        "ky": "Сиз азырынча каттала элексиз. /start жазыңыз",
    },
    "profile_title": {
        "ru": "Ваш профиль",
        "ky": "Сиздин профиль",
    },
    "profile_post_update": {
        "ru": "После отправки анкеты изменения делаются через удаление и повторное заполнение.",
        "ky": "Анкетаны жөнөткөндөн кийин өзгөртүү үчүн өчүрүп, кайра толтуруу керек.",
    },
    "update_info": {
        "ru": "После отправки анкеты редактирование делается так:\n1. Удаляете текущую анкету.\n2. Проходите регистрацию заново.\n\nЕсли готовы, нажмите кнопку ниже.",
        "ky": "Анкетаны жөнөткөндөн кийин өзгөртүү мындай болот:\n1. Учурдагы анкетаны өчүрөсүз.\n2. Кайра каттоодон өтөсүз.\n\nДаяр болсоңуз, төмөнкү баскычты басыңыз.",
    },
    "delete_confirm": {
        "ru": "Вы действительно хотите удалить свою анкету?\nПосле удаления нужно будет пройти регистрацию заново.",
        "ky": "Чын эле анкетаңызды өчүргүңүз келеби?\nӨчүргөндөн кийин кайра каттоодон өтүшүңүз керек болот.",
    },
    "delete_done": {
        "ru": "Ваша анкета удалена.\nНажмите кнопку ниже, чтобы заполнить её заново.",
        "ky": "Анкетаңыз өчүрүлдү.\nКайра толтуруу үчүн төмөнкү баскычты басыңыз.",
    },
    "delete_cancelled": {
        "ru": "Анкета не удалена.\nИспользуйте /profile, чтобы посмотреть профиль.",
        "ky": "Анкета өчүрүлгөн жок.\nПрофилди көрүү үчүн /profile колдонуңуз.",
    },
    "activity_missing_profile": {
        "ru": "Анкета не найдена. Если вы удаляли профиль, зарегистрируйтесь заново через /start.",
        "ky": "Анкета табылган жок. Эгер профилди өчүргөн болсоңуз, /start аркылуу кайра катталыңыз.",
    },
    "activity_unknown_option": {
        "ru": "Не удалось определить этот вариант ответа",
        "ky": "Бул жооп варианты аныкталган жок",
    },
    "activity_save_error": {
        "ru": "Не удалось сохранить ответ",
        "ky": "Жоопту сактоо мүмкүн болгон жок",
    },
    "activity_saved": {
        "ru": "Спасибо, статус обновлён.\n\n{title}: {label}\n\nЭта информация теперь отображается в вашей анкете на сайте Opus.",
        "ky": "Рахмат, статус жаңыртылды.\n\n{title}: {label}\n\nБул маалымат эми сиздин анкетада сайтта көрсөтүлөт.",
    },
    "skip": {
        "ru": "Пропустить",
        "ky": "Өткөрүп жиберүү",
    },
    "back": {
        "ru": "Назад",
        "ky": "Артка",
    },
}

CHOICE_TRANSLATIONS: dict[str, dict[str, dict[str, str]]] = {
    "gender": {
        "Мужчина": {"ru": "Мужчина", "ky": "Эркек"},
        "Женщина": {"ru": "Женщина", "ky": "Аял"},
    },
    "experience": {
        "Без опыта": {"ru": "Без опыта", "ky": "Тажрыйбасы жок"},
        "До 1 года": {"ru": "До 1 года", "ky": "1 жылга чейин"},
        "1–2 года": {"ru": "1–2 года", "ky": "1–2 жыл"},
        "2–5 лет": {"ru": "2–5 лет", "ky": "2–5 жыл"},
        "5+ лет": {"ru": "5+ лет", "ky": "5+ жыл"},
    },
    "employment_type": {
        "Подработки": {"ru": "Подработки", "ky": "Кошумча жумуш"},
        "Сезонная": {"ru": "Сезонная", "ky": "Сезондук"},
        "Постоянная работа": {"ru": "Постоянная работа", "ky": "Туруктуу иш"},
    },
    "schedule": {
        "Только будни": {"ru": "Только будни", "ky": "Иш күндөрү гана"},
        "Будни + выходные": {"ru": "Будни + выходные", "ky": "Иш күндөрү + дем алыш"},
        "Только выходные": {"ru": "Только выходные", "ky": "Дем алыш гана"},
        "Любые дни": {"ru": "Любые дни", "ky": "Каалаган күндөр"},
    },
    "sanitary_book": {
        "Есть": {"ru": "Есть", "ky": "Бар"},
        "Нет": {"ru": "Нет", "ky": "Жок"},
        "Готов(а) сделать": {"ru": "Готов(а) сделать", "ky": "Жасатууга даярмын"},
    },
    "contact_method": {
        "WhatsApp": {"ru": "WhatsApp", "ky": "WhatsApp"},
        "Обычный номер": {"ru": "Обычный номер", "ky": "Жөнөкөй номер"},
    },
}


def normalize_language(language: str | None) -> str:
    if language in SUPPORTED_LANGUAGES:
        return str(language)
    return DEFAULT_LANGUAGE


def infer_language(language_code: str | None) -> str:
    if language_code and language_code.lower().startswith("ky"):
        return "ky"
    return "ru"


def resolve_language(*, context_language: str | None = None, stored_language: str | None = None, telegram_language: str | None = None) -> str:
    return normalize_language(context_language or stored_language or infer_language(telegram_language))


def tr(language: str, key: str, **kwargs: object) -> str:
    lang = normalize_language(language)
    template = TEXTS.get(key, {}).get(lang) or TEXTS.get(key, {}).get(DEFAULT_LANGUAGE) or key
    return template.format(**kwargs)


def language_name(language: str) -> str:
    return LANGUAGE_NAMES[normalize_language(language)]


def localize_choice(language: str, category: str, value: str | None) -> str | None:
    if value is None:
        return None
    if category not in CHOICE_TRANSLATIONS:
        return value
    return CHOICE_TRANSLATIONS[category].get(value, {}).get(normalize_language(language), value)


def localize_csv_choices(language: str, category: str, value: str | None) -> str | None:
    if not value:
        return value
    items = [item.strip() for item in value.split(",") if item.strip()]
    localized_items = [localize_choice(language, category, item) or item for item in items]
    return ", ".join(localized_items)


def get_display_options(language: str, category: str, values: Iterable[str]) -> list[str]:
    return [localize_choice(language, category, value) or value for value in values]


def parse_choice_value(language: str, category: str, display_value: str) -> str | None:
    normalized_display = display_value.strip()
    if category not in CHOICE_TRANSLATIONS:
        return normalized_display

    for stored_value, translations in CHOICE_TRANSLATIONS[category].items():
        if normalized_display == stored_value:
            return stored_value
        if normalized_display == translations.get(normalize_language(language)):
            return stored_value
    return None
