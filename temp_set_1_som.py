import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://lgjrqvjwnrrpbmyxnsov.supabase.co/rest/v1/tariff_plans?select=*"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxnanJxdmp3bnJycGJteXhuc292Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDQ5NzgyNCwiZXhwIjoyMDkwMDczODI0fQ.d3jaPaIiQ35in2JW_9DemY0tnpEFw5s8yr5qBjBUJjw"

req = urllib.request.Request(url, method="GET")
req.add_header("apikey", key)
req.add_header("Authorization", f"Bearer {key}")

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        tariffs = json.loads(response.read().decode())
        print("Current tariffs:")
        for t in tariffs:
            print(f"ID: {t['id']}, Name: {t['name']}, Price: {t['price']}")

            update_url = f"https://lgjrqvjwnrrpbmyxnsov.supabase.co/rest/v1/tariff_plans?id=eq.{t['id']}"
            update_req = urllib.request.Request(update_url, data=json.dumps({"price": 1}).encode("utf-8"), method="PATCH")
            update_req.add_header("apikey", key)
            update_req.add_header("Authorization", f"Bearer {key}")
            update_req.add_header("Content-Type", "application/json")
            
            with urllib.request.urlopen(update_req, context=ctx) as up_res:
                print(f"Updated {t['name']} to 1")

except Exception as e:
    print(f"Error: {e}")
