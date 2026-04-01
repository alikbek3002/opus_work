import json
import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

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

    # Получаем тариф
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

    # Создаём запись платежа в нашей БД
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

    payment_id = payment.data[0]["id"]
    redirect_url = f"{settings.APP_URL.rstrip('/')}/tariffs?payment=success&payment_id={payment_id}"
    callback_base_url = settings.FINIK_WEBHOOK_URL or str(request.url_for("payment_callback"))
    callback_url = build_webhook_url(callback_base_url, payment_id)

    try:
        finik_result = create_payment_link(
            payment_id=payment_id,
            amount=int(tariff_data["price"]),
            redirect_url=redirect_url,
            webhook_url=callback_url,
            description=tariff_data.get("description") or tariff_data.get("name"),
        )
    except FinikConfigError as exc:
        supabase.table("payments").update({"status": "failed"}).eq("id", payment_id).execute()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except FinikRequestError as exc:
        supabase.table("payments").update({"status": "failed"}).eq("id", payment_id).execute()
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    update_payload: Dict[str, str] = {"status": "pending"}
    if finik_result.finik_payment_id:
        update_payload["fenik_payment_id"] = finik_result.finik_payment_id

    supabase.table("payments").update(update_payload).eq("id", payment_id).execute()

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
                status_code=500,
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
            raise HTTPException(status_code=500, detail=str(exc)) from exc

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
            raise HTTPException(status_code=500, detail="Тариф платежа не найден")

        period_days = 7 if tariff["period"] == "week" else 30
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
            "starts_at": starts_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "is_active": True,
        }).execute()

        try:
            bot_token = settings.BOT_TOKEN
            employer_id = payment_data["employer_id"]
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            message_text = "🎉 Вы успешно приобрели тариф и подписка активирована!\n\n🔥 Успейте купить еще в следующий раз — осталось всего 28 тарифов по скидке для первых зарегистрированных пользователей!"
            requests.post(telegram_url, json={"chat_id": employer_id, "text": message_text}, timeout=5)
        except Exception as e:
            logger.error("Failed to send telegram notification: %s", e)

        return {"status": "ok", "message": "Подписка активирована"}

    if _is_failed_status(callback_status):
        return {"status": "ok", "message": "Платёж отклонён"}

    return {"status": "ok", "message": "Статус callback принят"}
