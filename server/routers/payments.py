import json
import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from config import settings
from database import supabase
from middleware.auth import get_current_user
from models.schemas import CreatePaymentRequest, PaymentResponse
from services.finik import (
    FinikConfigError,
    FinikRequestError,
    build_webhook_url,
    create_payment_link,
    is_webhook_verification_configured,
    verify_webhook_signature,
)

router = APIRouter(prefix="/api/payments", tags=["Платежи"])
logger = logging.getLogger(__name__)


def _safe_mark_payment_failed(payment_id: Optional[str]) -> None:
    if not payment_id:
        return
    try:
        supabase.table("payments").update({"status": "failed"}).eq("id", payment_id).execute()
    except Exception as exc:
        logger.error("Не удалось обновить статус платежа %s на failed: %s", payment_id, exc)


def _get_public_base_url(request: Request) -> str:
    origin = request.headers.get("origin")
    if origin:
        parsed_origin = urlsplit(origin)
        if parsed_origin.scheme in {"http", "https"} and parsed_origin.netloc:
            return f"{parsed_origin.scheme}://{parsed_origin.netloc}"

    forwarded_proto = request.headers.get("x-forwarded-proto")
    forwarded_host = request.headers.get("x-forwarded-host")
    if forwarded_proto and forwarded_host:
        return f"{forwarded_proto}://{forwarded_host}"

    return str(request.base_url).rstrip("/")


def _get_app_base_url(request: Request) -> str:
    configured_app_url = settings.APP_URL.strip()
    if configured_app_url and configured_app_url != "http://localhost:5173":
        return configured_app_url.rstrip("/")
    return _get_public_base_url(request)


def _get_callback_base_url(request: Request) -> str:
    if settings.FINIK_WEBHOOK_URL:
        return settings.FINIK_WEBHOOK_URL

    public_base_url = _get_public_base_url(request)
    return f"{public_base_url.rstrip('/')}{request.app.url_path_for('payment_callback')}"


def _ensure_employer_exists(current_user: dict) -> None:
    employer_id = current_user["id"]
    email = current_user.get("email") or ""
    fallback_name = email.split("@")[0] if email else "Работодатель"

    existing_employer = (
        supabase.table("employers")
        .select("id")
        .eq("id", employer_id)
        .limit(1)
        .execute()
    )
    if existing_employer.data:
        return

    supabase.table("employers").upsert({
        "id": employer_id,
        "full_name": fallback_name,
        "email": email or f"{employer_id}@placeholder.local",
        "company_name": None,
    }).execute()


def _is_success_status(status: str) -> bool:
    return status.upper() in {"SUCCEEDED", "SUCCESS", "PAID", "COMPLETED"}


def _is_failed_status(status: str) -> bool:
    return status.upper() in {"FAILED", "FAIL", "DECLINED", "CANCELED", "CANCELLED", "ERROR"}


def _get_payment_for_callback(
    payment_id: Optional[str],
    transaction_id: Optional[str],
) -> Optional[dict]:
    if payment_id:
        response_by_id = (
            supabase.table("payments")
            .select("*, tariff_plans(*)")
            .eq("id", payment_id)
            .limit(1)
            .execute()
        )
        if response_by_id.data:
            return response_by_id.data[0]

    if transaction_id:
        response_by_finik_id = (
            supabase.table("payments")
            .select("*, tariff_plans(*)")
            .eq("fenik_payment_id", transaction_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if response_by_finik_id.data:
            return response_by_finik_id.data[0]

    return None


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    request: Request,
    data: CreatePaymentRequest,
    current_user: dict = Depends(get_current_user),
):
    """Создать платёж для покупки тарифа."""
    employer_id = current_user["id"]
    payment_id: Optional[str] = None

    try:
        _ensure_employer_exists(current_user)

        tariff_response = (
            supabase.table("tariff_plans")
            .select("*")
            .eq("id", data.tariff_id)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )

        tariff_data = tariff_response.data[0] if tariff_response.data else None
        if not tariff_data:
            raise HTTPException(status_code=404, detail="Тариф не найден")

        payment = (
            supabase.table("payments")
            .insert({
                "employer_id": employer_id,
                "tariff_id": data.tariff_id,
                "amount": tariff_data["price"],
                "status": "pending",
            })
            .execute()
        )

        created_payment = payment.data[0] if payment.data else None
        payment_id = created_payment["id"] if created_payment else None
        if not payment_id:
            logger.error("Supabase не вернул id после создания платежа: %s", payment.data)
            raise HTTPException(status_code=502, detail="Не удалось создать запись платежа")

        app_base_url = _get_app_base_url(request)
        redirect_url = f"{app_base_url}/tariffs?payment=success&payment_id={payment_id}"
        callback_base_url = _get_callback_base_url(request)
        callback_url = build_webhook_url(callback_base_url, payment_id)

        finik_result = create_payment_link(
            payment_id=payment_id,
            amount=int(tariff_data["price"]),
            redirect_url=redirect_url,
            webhook_url=callback_url,
            description=tariff_data.get("description") or tariff_data.get("name"),
        )
    except FinikConfigError as exc:
        _safe_mark_payment_failed(payment_id)
        logger.exception("Finik конфиг не настроен для платежа %s", payment_id)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except FinikRequestError as exc:
        _safe_mark_payment_failed(payment_id)
        logger.warning("Finik отклонил создание платежа %s: %s", payment_id, exc)
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except HTTPException:
        _safe_mark_payment_failed(payment_id)
        raise
    except Exception as exc:
        _safe_mark_payment_failed(payment_id)
        logger.exception("Неожиданная ошибка при создании платежа для employer_id=%s", employer_id)
        raise HTTPException(status_code=502, detail="Не удалось создать платеж") from exc

    update_payload: Dict[str, str] = {"status": "pending"}
    if finik_result.finik_payment_id:
        update_payload["fenik_payment_id"] = finik_result.finik_payment_id

    try:
        supabase.table("payments").update(update_payload).eq("id", payment_id).execute()
    except Exception as exc:
        logger.exception("Не удалось обновить платёж %s после ответа Finik", payment_id)
        raise HTTPException(status_code=502, detail="Платёж создан, но не удалось сохранить его статус") from exc

    return PaymentResponse(
        payment_id=payment_id,
        payment_url=finik_result.payment_url,
        status="pending",
    )


@router.post("/callback", name="payment_callback")
async def payment_callback(
    request: Request,
    payment_id: Optional[str] = Query(default=None),
):
    """
    Webhook от Finik Acquiring — вызывается после успешной/неуспешной оплаты.
    """
    raw_body = await request.body()
    try:
        payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Некорректный JSON в callback Finik") from exc

    signature = request.headers.get("signature")
    if settings.FINIK_VERIFY_SIGNATURE:
        if not signature:
            raise HTTPException(status_code=401, detail="Отсутствует подпись callback")
        if not is_webhook_verification_configured():
            raise HTTPException(
                status_code=503,
                detail="FINIK_VERIFY_SIGNATURE=true, но не задан публичный ключ Finik",
            )
        try:
            is_valid_signature = verify_webhook_signature(
                http_method=request.method,
                path=request.url.path,
                query_string=request.url.query,
                headers=dict(request.headers),
                body=payload,
                signature=signature,
            )
        except FinikConfigError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        if not is_valid_signature:
            raise HTTPException(status_code=401, detail="Некорректная подпись callback Finik")

    callback_payment_id = payment_id or payload.get("PaymentId") or payload.get("paymentId")
    callback_payment_id = str(callback_payment_id) if callback_payment_id else None

    transaction_id = payload.get("transactionId") or payload.get("id")
    transaction_id = str(transaction_id) if transaction_id else None

    callback_status = str(payload.get("status", "")).upper()

    payment_data = _get_payment_for_callback(callback_payment_id, transaction_id)
    if not payment_data:
        logger.warning(
            "Finik callback: платеж не найден (payment_id=%s, transaction_id=%s)",
            callback_payment_id,
            transaction_id,
        )
        return {"status": "ok", "message": "Callback принят, платёж не найден"}

    current_payment_id = payment_data["id"]

    if payment_data.get("status") == "success":
        return {"status": "ok", "message": "Платёж уже обработан"}

    update_data: Dict[str, str] = {}
    if transaction_id:
        update_data["fenik_payment_id"] = transaction_id
    if _is_success_status(callback_status):
        update_data["status"] = "success"
    elif _is_failed_status(callback_status):
        update_data["status"] = "failed"

    if update_data:
        supabase.table("payments").update(update_data).eq("id", current_payment_id).execute()

    if _is_success_status(callback_status):
        tariff = payment_data.get("tariff_plans")
        if not tariff:
            raise HTTPException(status_code=502, detail="Тариф платежа не найден")

        period_days = {
            "day": 3,
            "week": 7,
            "month": 30,
            "quarter": 90,
        }.get(tariff["period"], 30)
        starts_at = datetime.now(timezone.utc)
        expires_at = starts_at + timedelta(days=period_days)

        # Оставляем только одну активную подписку для работодателя.
        supabase.table("subscriptions").update(
            {"is_active": False}
        ).eq("employer_id", payment_data["employer_id"]).eq("is_active", True).execute()

        supabase.table("subscriptions").insert({
            "employer_id": payment_data["employer_id"],
            "tariff_id": tariff["id"],
            "cards_remaining": tariff["card_limit"],
            "daily_limit": tariff.get("daily_limit"),
            "daily_views_used": 0,
            "daily_views_remaining": tariff.get("daily_limit"),
            "starts_at": starts_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "is_active": True,
        }).execute()

        try:
            bot_token = settings.BOT_TOKEN
            employer_id = payment_data["employer_id"]
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            message_text = (
                "🎉 Вы успешно приобрели тариф и подписка активирована!\n\n"
                "🔥 Ранний доступ: скидка действует для первых 50 заказчиков и сохраняется при продлении."
            )
            requests.post(telegram_url, json={"chat_id": employer_id, "text": message_text}, timeout=5)
        except Exception as e:
            logger.error("Failed to send telegram notification: %s", e)

        return {"status": "ok", "message": "Подписка активирована"}

    if _is_failed_status(callback_status):
        return {"status": "ok", "message": "Платёж отклонён"}

    return {"status": "ok", "message": "Статус callback принят"}
