import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'server'))

try:
    from database import supabase
except Exception as e:
    print(f"Error importing supabase: {e}")
    sys.exit(1)

response = supabase.table("tariff_plans").select("*").execute()
tariffs = response.data

print("Current tariffs:")
for t in tariffs:
    print(f"ID: {t['id']}, Name: {t['name']}, Price: {t['price']}")

print("\nUpdating prices to 1...")
for t in tariffs:
    supabase.table("tariff_plans").update({"price": 1}).eq("id", t["id"]).execute()

print("Prices updated successfully.")
