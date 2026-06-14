"""Quick DB connection test."""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv(override=True)
url = os.getenv("DATABASE_URL")
print(f"🔗 Connecting to: {url}")

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ Connection successful!")
        print(f"📦 PostgreSQL: {version}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
