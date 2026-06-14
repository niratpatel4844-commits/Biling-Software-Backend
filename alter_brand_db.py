from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as con:
        # Add brand_code column if it doesn't exist
        con.execute(text("ALTER TABLE brands ADD COLUMN IF NOT EXISTS brand_code VARCHAR(100);"))
        con.commit()
    print("Brands table updated successfully with brand_code.")
except Exception as e:
    print("Migration failed:", e)
