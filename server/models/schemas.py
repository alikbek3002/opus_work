from pydantic import BaseModel, EmailStr
from typing import Literal, Optional
from datetime import datetime


# === Auth ===

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    email: str


# === Employee ===

VerificationStatus = Literal["pending", "verified", "rejected"]
ActivitySignal = Literal["high", "medium", "low"]

class EmployeeCard(BaseModel):
    """Базовая карточка — видна без оплаты."""
    id: str
    full_name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    district: Optional[str] = None
    specializations: Optional[str] = None
    experience: Optional[str] = None
    employment_type: Optional[str] = None
    schedule: Optional[str] = None
    opus_experience: Optional[str] = None
    is_verified: bool = False
    verification_status: VerificationStatus = "pending"
    verification_decided_at: Optional[datetime] = None
    activity_signal: Optional[ActivitySignal] = None
    activity_signal_updated_at: Optional[datetime] = None
    contact_opens_count: int = 0
    telegram_id: Optional[int] = None


class EmployeeFullProfile(EmployeeCard):
    """Полный профиль — доступен после оплаты просмотра."""
    telegram_username: Optional[str] = None
    phone_number: Optional[str] = None
    has_whatsapp: Optional[bool] = None
    photo_file_id: Optional[str] = None
    ready_for_weekends: Optional[bool] = None
    has_sanitary_book: Optional[str] = None
    about_me: Optional[str] = None
    has_recommendations: Optional[bool] = None
    verification_rejected_reason: Optional[str] = None
    verified_by_telegram_id: Optional[int] = None
    created_at: Optional[datetime] = None



class ViewedEmployeeHistoryItem(EmployeeFullProfile):
    """Карточка сотрудника, уже открытая работодателем."""
    viewed_at: datetime


# === Tariff ===

class TariffPlan(BaseModel):
    id: str
    name: str
    period: str
    card_limit: int
    daily_limit: Optional[int] = None
    price: int
    description: Optional[str] = None


# === Subscription ===

class Subscription(BaseModel):
    id: str
    tariff_id: str
    cards_remaining: int
    daily_limit: Optional[int] = None
    daily_views_used: Optional[int] = None
    daily_views_remaining: Optional[int] = None
    starts_at: datetime
    expires_at: datetime
    is_active: bool


class SubscriptionDetails(Subscription):
    tariff_plans: Optional[TariffPlan] = None


# === Payment ===

class CreatePaymentRequest(BaseModel):
    tariff_id: str


class PaymentResponse(BaseModel):
    payment_id: str
    payment_url: Optional[str] = None
    status: str
