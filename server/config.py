import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    RAILWAY_DATABASE_URL: str = os.getenv("RAILWAY_DATABASE_URL", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-jwt-secret-key")
    FENIK_PAY_API_KEY: str = os.getenv("FENIK_PAY_API_KEY", "")
    FENIK_PAY_MERCHANT_ID: str = os.getenv("FENIK_PAY_MERCHANT_ID", "")
    FENIK_API_BASE_URL: str = os.getenv("FENIK_API_BASE_URL", "https://api.acquiring.averspay.kg")
    FENIK_ACCOUNT_ID: str = os.getenv("FENIK_ACCOUNT_ID", "")
    FENIK_MERCHANT_CATEGORY_CODE: str = os.getenv("FENIK_MERCHANT_CATEGORY_CODE", "0742")
    FENIK_QR_NAME: str = os.getenv("FENIK_QR_NAME", "Opus")
    FENIK_PRIVATE_KEY: str = os.getenv("FENIK_PRIVATE_KEY", "")
    FENIK_PRIVATE_KEY_PATH: str = os.getenv("FENIK_PRIVATE_KEY_PATH", "")
    FENIK_PUBLIC_KEY: str = os.getenv("FENIK_PUBLIC_KEY", "")
    FENIK_PUBLIC_KEY_PATH: str = os.getenv("FENIK_PUBLIC_KEY_PATH", "")
    FENIK_WEBHOOK_URL: str = os.getenv("FENIK_WEBHOOK_URL", "")
    FENIK_REQUEST_TIMEOUT_SEC: int = int(os.getenv("FENIK_REQUEST_TIMEOUT_SEC", "20"))
    FENIK_VERIFY_SIGNATURE: bool = os.getenv("FENIK_VERIFY_SIGNATURE", "false").lower() == "true"
    APP_URL: str = os.getenv("APP_URL", "http://localhost:5173")
    CRON_SECRET: str = os.getenv("CRON_SECRET", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Opus")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173,https://opus-work.org,https://www.opus-work.org").split(",")


settings = Settings()
