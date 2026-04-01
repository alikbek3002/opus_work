import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    VERIFICATION_BOT_TOKEN: str = os.getenv("VERIFICATION_BOT_TOKEN", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    def validate(self):
        if not self.VERIFICATION_BOT_TOKEN:
            raise ValueError("VERIFICATION_BOT_TOKEN не установлен в .env")
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL не установлен в .env")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_SERVICE_KEY не установлен в .env")


settings = Settings()
