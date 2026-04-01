from datetime import datetime, timedelta, timezone
from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

PART_TIME_EMPLOYMENT = "Подработка"
FULL_TIME_EMPLOYMENT = "Полная занятость"

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


def get_activity_signal_meta(employment_type: str | None, signal: str | None) -> dict[str, str] | None:
    if not employment_type or not signal:
        return None

    employment_meta = ACTIVITY_SIGNAL_META.get(employment_type)
    if not employment_meta:
        return None

    labels = employment_meta["labels"]
    if signal not in labels:
        return None

    return {
        "title": str(employment_meta["title"]),
        "label": str(labels[signal]),
    }


def get_activity_placeholder(employment_type: str | None) -> dict[str, str] | None:
    employment_meta = ACTIVITY_SIGNAL_META.get(employment_type or "")
    if not employment_meta:
        return None
    return {
        "title": str(employment_meta["title"]),
        "label": "Статус ещё не обновлялся",
    }


def build_activity_signal_keyboard(employment_type: str | None) -> InlineKeyboardMarkup | None:
    employment_meta = ACTIVITY_SIGNAL_META.get(employment_type or "")
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


def build_activity_signal_prompt(full_name: str | None, employment_type: str | None) -> str | None:
    employment_meta = ACTIVITY_SIGNAL_META.get(employment_type or "")
    if not employment_meta:
        return None

    safe_name = escape(full_name or "Здравствуйте")
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
    )
    if meta:
        return f"{meta['title']}: {meta['label']}"

    placeholder = get_activity_placeholder(employee.get("employment_type"))
    if placeholder:
        return f"{placeholder['title']}: {placeholder['label']}"

    return None
