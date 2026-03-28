from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timedelta
from database import supabase
from middleware.auth import get_current_user
from models.schemas import CreatePaymentRequest, PaymentResponse, FenikPayCallback

router = APIRouter(prefix="/api/payments", tags=["Платежи"])


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    data: CreatePaymentRequest,
    current_user: dict = Depends(get_current_user),
):
    """Создать платёж для покупки тарифа."""
    employer_id = current_user["id"]

    # Получаем тариф
    tariff = (
        supabase.table("tariff_plans")
        .select("*")
        .eq("id", data.tariff_id)
        .single()
        .execute()
    )

    if not tariff.data:
        raise HTTPException(status_code=404, detail="Тариф не найден")

    tariff_data = tariff.data

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

    # TODO: Интеграция с Fenik Pay API
    # Здесь нужно отправить запрос на создание платежа в Fenik Pay
    # и получить URL для перенаправления пользователя на оплату
    #
    # Пример:
    # fenik_response = requests.post("https://api.fenikpay.kg/payments", json={
    #     "merchant_id": settings.FENIK_PAY_MERCHANT_ID,
    #     "amount": tariff_data["price"],
    #     "order_id": payment_id,
    #     "callback_url": "https://your-domain.com/api/payments/callback",
    #     "return_url": "https://your-domain.com/tariffs?payment=success",
    # })
    # payment_url = fenik_response.json()["payment_url"]

    payment_url = None  # Заглушка — будет заменена на URL Fenik Pay

    return PaymentResponse(
        payment_id=payment_id,
        payment_url=payment_url,
        status="pending",
    )


@router.post("/callback")
async def payment_callback(callback: FenikPayCallback):
    """
    Webhook от Fenik Pay — вызывается после успешной/неуспешной оплаты.
    """
    # TODO: Верифицировать подпись запроса от Fenik Pay

    # Находим платёж
    payment = (
        supabase.table("payments")
        .select("*, tariff_plans(*)")
        .eq("id", callback.payment_id)
        .single()
        .execute()
    )

    if not payment.data:
        raise HTTPException(status_code=404, detail="Платёж не найден")

    payment_data = payment.data

    if callback.status == "success":
        # Обновляем статус платежа
        supabase.table("payments").update({
            "status": "success",
            "fenik_payment_id": callback.transaction_id,
        }).eq("id", callback.payment_id).execute()

        # Создаём подписку
        tariff = payment_data["tariff_plans"]
        period_days = 7 if tariff["period"] == "week" else 30

        supabase.table("subscriptions").insert({
            "employer_id": payment_data["employer_id"],
            "tariff_id": tariff["id"],
            "cards_remaining": tariff["card_limit"],
            "starts_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=period_days)).isoformat(),
            "is_active": True,
        }).execute()

        return {"status": "ok", "message": "Подписка активирована"}

    elif callback.status == "failed":
        supabase.table("payments").update({
            "status": "failed",
            "fenik_payment_id": callback.transaction_id,
        }).eq("id", callback.payment_id).execute()

        return {"status": "ok", "message": "Платёж отклонён"}

    return {"status": "ok"}
