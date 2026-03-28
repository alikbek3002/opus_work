from supabase import create_client, Client
from config import settings

# Клиент с service role key (полный доступ для сервера)
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Клиент с anon key (для операций от имени пользователя)
supabase_anon: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
