from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as con:
        con.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS category_code VARCHAR(100);"))
        con.commit()
    print("Categories table updated successfully with category_code.")
except Exception as e:
    print("Migration failed:", e)
