import os
import psycopg2
from dotenv import load_dotenv

load_dotenv("server/.env")

db_url = os.environ.get("RAILWAY_DATABASE_URL")
if not db_url:
    print("Database URL not found in server/.env")
    exit(1)

valid_url = db_url.replace("postgresql://", "postgres://")

try:
    conn = psycopg2.connect(valid_url)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS has_sanitary_book VARCHAR(255);")
    print("SUCCESS: Column has_sanitary_book added successfully.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Connection error: {e}")
