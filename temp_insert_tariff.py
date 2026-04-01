import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://lgjrqvjwnrrpbmyxnsov.supabase.co/rest/v1/tariff_plans"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxnanJxdmp3bnJycGJteXhuc292Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDQ5NzgyNCwiZXhwIjoyMDkwMDczODI0fQ.d3jaPaIiQ35in2JW_9DemY0tnpEFw5s8yr5qBjBUJjw"

tariff_data = {
    "name": "1 День",
    "price": 490,
    "card_limit": 3,
    "period": "day",
    "is_active": True,
    "description": "Тариф на 1 день"
}

req = urllib.request.Request(url, data=json.dumps(tariff_data).encode("utf-8"), method="POST")
req.add_header("apikey", key)
req.add_header("Authorization", f"Bearer {key}")
req.add_header("Content-Type", "application/json")
req.add_header("Prefer", "return=minimal")

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        print("Tariff inserted successfully")
except Exception as e:
    print(f"Error inserting: {e}")
