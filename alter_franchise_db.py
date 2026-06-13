from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as con:
        con.execute(text("ALTER TABLE franchises ADD COLUMN country VARCHAR(100) DEFAULT 'India';"))
        con.commit()
    print("Added country column to franchises.")
except Exception as e:
    print("Error:", e)
