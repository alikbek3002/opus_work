from datetime import datetime, timedelta, timezone
from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from i18n import normalize_language

PART_TIME_EMPLOYMENT = "Подработки"
FULL_TIME_EMPLOYMENT = "Постоянная работа"
SEASONAL_EMPLOYMENT = "Сезонная"

PROMPT_INTERVAL = timedelta(hours=72)
PROMPT_SCAN_INTERVAL_SECONDS = 60 * 60

ACTIVITY_SIGNAL_META: dict[str, dict[str, object]] = {
    PART_TIME_EMPLOYMENT: {
        "title": "Готовность к смене",
        "question": "Насколько вы готовы выйти на смену в ближайшие дни?",
        "options": [
            ("high", "Могу выйти сегодня или завтра"),
            ("medium", "Могу выйти в ближайшие дни"),
            ("low", "Пока рассматриваю выборочно"),
        ],
        "labels": {
            "high": "Готов(а) выйти сегодня или завтра",
            "medium": "Может выйти в ближайшие дни",
            "low": "Выходит выборочно",
        },
    },
    FULL_TIME_EMPLOYMENT: {
        "title": "Активность поиска работы",
        "question": "Насколько активно вы сейчас ищете постоянную работу?",
        "options": [
            ("high", "Ищу работу активно сейчас"),
            ("medium", "Рассматриваю хорошие предложения"),
            ("low", "Пока без спешки, но открыт(а)"),
        ],
        "labels": {
            "high": "Активно ищет работу",
            "medium": "Рассматривает хорошие предложения",
            "low": "Ищет без спешки",
        },
    },
}

ACTIVITY_SIGNAL_META_KY: dict[str, dict[str, object]] = {
    PART_TIME_EMPLOYMENT: {
        "title": "Сменага даярдык",
        "question": "Жакынкы күндөрү сменага канчалык даярсыз?",
        "options": [
            ("high", "Бүгүн же эртең чыга алам"),
            ("medium", "Жакынкы күндөрү чыга алам"),
            ("low", "Азырынча тандап карап жатам"),
        ],
        "labels": {
            "high": "Бүгүн же эртең чыга алат",
            "medium": "Жакынкы күндөрү чыга алат",
            "low": "Тандап чыгат",
        },
    },
    FULL_TIME_EMPLOYMENT: {
        "title": "Жумуш издөө активдүүлүгү",
        "question": "Азыр туруктуу жумушту канчалык активдүү издеп жатасыз?",
        "options": [
            ("high", "Азыр активдүү издеп жатам"),
            ("medium", "Жакшы сунуштарды карайм"),
            ("low", "Шашылбайм, бирок ачыкмын"),
        ],
        "labels": {
            "high": "Жумушту активдүү издеп жатат",
            "medium": "Жакшы сунуштарды карайт",
            "low": "Шашылбай издеп жатат",
        },
    },
}


def get_activity_bundle(language: str) -> dict[str, dict[str, object]]:
    return ACTIVITY_SIGNAL_META_KY if normalize_language(language) == "ky" else ACTIVITY_SIGNAL_META


def resolve_activity_employment_type(employment_type: str | None) -> str | None:
    if not employment_type:
        return None

    values = {
        item.strip().lower()
        for item in str(employment_type).split(",")
        if item and item.strip()
    }
    if not values:
        return None

    if any("постоян" in value for value in values):
        return FULL_TIME_EMPLOYMENT

    if any("подработ" in value for value in values):
        return PART_TIME_EMPLOYMENT

    if any("сезон" in value for value in values):
        return PART_TIME_EMPLOYMENT

    return None


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def get_activity_signal_meta(employment_type: str | None, signal: str | None, language: str = "ru") -> dict[str, str] | None:
    if not employment_type or not signal:
        return None

    resolved_employment_type = resolve_activity_employment_type(employment_type)
    employment_meta = get_activity_bundle(language).get(resolved_employment_type or "")
    if not employment_meta:
        return None

    labels = employment_meta["labels"]
    if signal not in labels:
        return None

    return {
        "title": str(employment_meta["title"]),
        "label": str(labels[signal]),
    }


def get_activity_prompt_meta(employment_type: str | None, language: str = "ru") -> dict[str, object] | None:
    resolved_employment_type = resolve_activity_employment_type(employment_type)
    employment_meta = get_activity_bundle(language).get(resolved_employment_type or "")
    if not employment_meta:
        return None
    return {
        "title": str(employment_meta["title"]),
        "question": str(employment_meta["question"]),
        "options": list(employment_meta["options"]),
    }


def parse_activity_signal_choice(employment_type: str | None, display_value: str, language: str = "ru") -> str | None:
    employment_meta = get_activity_prompt_meta(employment_type, language)
    if not employment_meta:
        return None

    normalized_display = display_value.strip()
    for option_value, option_label in employment_meta["options"]:
        if normalized_display == str(option_label):
            return str(option_value)
    return None


def get_activity_placeholder(employment_type: str | None, language: str = "ru") -> dict[str, str] | None:
    resolved_employment_type = resolve_activity_employment_type(employment_type)
    employment_meta = get_activity_bundle(language).get(resolved_employment_type or "")
    if not employment_meta:
        return None
    return {
        "title": str(employment_meta["title"]),
        "label": "Статус ещё не обновлялся",
    }


def build_activity_signal_keyboard(employment_type: str | None, language: str = "ru") -> InlineKeyboardMarkup | None:
    resolved_employment_type = resolve_activity_employment_type(employment_type)
    employment_meta = get_activity_bundle(language).get(resolved_employment_type or "")
    if not employment_meta:
        return None

    keyboard = [
        [
            InlineKeyboardButton(
                str(option_label),
                callback_data=f"activity_signal:{option_value}",
            )
        ]
        for option_value, option_label in employment_meta["options"]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_activity_signal_prompt(full_name: str | None, employment_type: str | None, language: str = "ru") -> str | None:
    resolved_employment_type = resolve_activity_employment_type(employment_type)
    employment_meta = get_activity_bundle(language).get(resolved_employment_type or "")
    if not employment_meta:
        return None

    safe_name = escape(full_name or "Здравствуйте")
    if normalize_language(language) == "ky":
        return (
            f"👋 {safe_name}, статусуңузду жаңыртып коюңуз.\n\n"
            f"<b>{escape(str(employment_meta['question']))}</b>\n\n"
            "Бул жооп анкетаңызда сайтта көрүнүп, иш берүүчүлөргө актуалдуулугуңузду жакшыраак түшүнүүгө жардам берет."
        )

    return (
        f"👋 {safe_name}, обновите, пожалуйста, ваш статус.\n\n"
        f"<b>{escape(str(employment_meta['question']))}</b>\n\n"
        "Ответ появится в вашей анкете на сайте и поможет работодателям лучше понять вашу актуальность."
    )


def is_activity_prompt_due(prompted_at: str | None, *, now: datetime | None = None) -> bool:
    current_time = now or datetime.now(timezone.utc)
    parsed_prompted_at = parse_iso_datetime(prompted_at)
    if parsed_prompted_at is None:
        return True
    return parsed_prompted_at <= current_time - PROMPT_INTERVAL


def format_employee_activity_status(employee: dict) -> str | None:
    meta = get_activity_signal_meta(
        employee.get("employment_type"),
        employee.get("activity_signal"),
        employee.get("preferred_language") or "ru",
    )
    if meta:
        return f"{meta['title']}: {meta['label']}"

    placeholder = get_activity_placeholder(employee.get("employment_type"), employee.get("preferred_language") or "ru")
    if placeholder:
        return f"{placeholder['title']}: {placeholder['label']}"

    return None
