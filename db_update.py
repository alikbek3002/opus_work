import os
import psycopg2
from dotenv import load_dotenv

load_dotenv("server/.env")

db_url = os.environ.get("RAILWAY_DATABASE_URL")
if not db_url:
    print("Database URL not found in .env")
    exit(1)

valid_url = db_url.replace("postgresql://", "postgres://")

try:
    conn = psycopg2.connect(valid_url)
    conn.autocommit = True
    cursor = conn.cursor()

    # 1. Add schedule column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS schedule TEXT;")
        print("Schema altered successfully for 'schedule' column.")
    except Exception as e:
        print(f"Error altering schema for schedule: {e}")

    # 2. Insert the new 1-day tariff
    # Columns typically: id, name, price, card_limit, period, is_active
    cursor.execute("""
        INSERT INTO tariff_plans (name, price, card_limit, period, is_active, description)
        VALUES ('1 День', 490, 3, 'day', true, 'Тариф на 1 день')
        ON CONFLICT (name, period) DO NOTHING;
    """)
    print("1-day tariff inserted or already exists.")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Connection error: {e}")
