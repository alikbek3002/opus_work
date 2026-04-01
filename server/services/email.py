import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

from config import settings


def email_is_configured() -> bool:
    """Проверяет, настроена ли SMTP-отправка."""
    return bool(settings.SMTP_HOST and settings.SMTP_FROM_EMAIL)


def send_email(recipient: str, subject: str, text_body: str, html_body: Optional[str] = None) -> None:
    """Отправляет email через SMTP."""
    if not email_is_configured():
        raise RuntimeError(
            "SMTP не настроен. Укажите SMTP_HOST и SMTP_FROM_EMAIL в server/.env."
        )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = (
        f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        if settings.SMTP_FROM_NAME
        else settings.SMTP_FROM_EMAIL
    )
    message["To"] = recipient
    message.set_content(text_body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    if settings.SMTP_PORT == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context) as smtp:
            if settings.SMTP_USERNAME:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
        return

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.ehlo()
        if settings.SMTP_USE_TLS:
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
        if settings.SMTP_USERNAME:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(message)
