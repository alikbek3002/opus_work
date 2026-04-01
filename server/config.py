import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def _getenv(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def _resolve_default_key_path(filename: str) -> str:
    candidate = BASE_DIR / "keys" / filename
    if candidate.exists():
        return str(candidate)
    return ""


class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    RAILWAY_DATABASE_URL: str = os.getenv("RAILWAY_DATABASE_URL", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-jwt-secret-key")
    FINIK_API_KEY: str = _getenv("FINIK_API_KEY", "FENIK_API_KEY")
    FINIK_API_BASE_URL: str = _getenv(
        "FINIK_API_BASE_URL",
        "FENIK_API_BASE_URL",
        default="https://api.acquiring.averspay.kg",
    )
    FINIK_ACCOUNT_ID: str = _getenv("FINIK_ACCOUNT_ID", "FENIK_ACCOUNT_ID")
    FINIK_PRIVATE_KEY: str = _getenv("FINIK_PRIVATE_KEY", "FENIK_PRIVATE_KEY")
    FINIK_PRIVATE_KEY_BASE64: str = _getenv(
        "FINIK_PRIVATE_KEY_BASE64",
        "FINIK_PRIVATE_KEY_B64",
        "FENIK_PRIVATE_KEY_BASE64",
        "FENIK_PRIVATE_KEY_B64",
    )
    FINIK_PRIVATE_KEY_PATH: str = _getenv(
        "FINIK_PRIVATE_KEY_PATH",
        "FENIK_PRIVATE_KEY_PATH",
        default=_resolve_default_key_path("finik_private.pem"),
    )
    FINIK_PUBLIC_KEY: str = _getenv("FINIK_PUBLIC_KEY", "FENIK_PUBLIC_KEY")
    FINIK_PUBLIC_KEY_BASE64: str = _getenv(
        "FINIK_PUBLIC_KEY_BASE64",
        "FINIK_PUBLIC_KEY_B64",
        "FENIK_PUBLIC_KEY_BASE64",
        "FENIK_PUBLIC_KEY_B64",
    )
    FINIK_PUBLIC_KEY_PATH: str = _getenv(
        "FINIK_PUBLIC_KEY_PATH",
        "FENIK_PUBLIC_KEY_PATH",
        default=_resolve_default_key_path("finik_public.pem"),
    )
    FINIK_WEBHOOK_URL: str = _getenv("FINIK_WEBHOOK_URL", "FENIK_WEBHOOK_URL")
    FINIK_VERIFY_SIGNATURE: bool = _getenv(
        "FINIK_VERIFY_SIGNATURE",
        "FENIK_VERIFY_SIGNATURE",
        default="false",
    ).lower() == "true"
    APP_URL: str = os.getenv("APP_URL", "http://localhost:5173")
    CRON_SECRET: str = os.getenv("CRON_SECRET", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Opus")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    _cors_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,https://opus-work.org,https://www.opus-work.org")
    CORS_ORIGINS: list = [origin.strip() for origin in _cors_env.split(",") if origin.strip()]
    
    def __init__(self):
        # Always ensure these origins are allowed
        default_origins = ["http://localhost:5173", "https://opus-work.org", "https://www.opus-work.org"]
        for origin in default_origins:
            if origin not in self.CORS_ORIGINS:
                self.CORS_ORIGINS.append(origin)


settings = Settings()
