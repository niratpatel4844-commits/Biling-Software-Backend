from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as con:
        con.execute(text("ALTER TABLE branches ADD COLUMN mobile VARCHAR(20);"))
        con.execute(text("ALTER TABLE branches ADD COLUMN country VARCHAR(100) DEFAULT 'India';"))
        con.commit()
    print("Added mobile and country columns to branches.")
except Exception as e:
    print("Error:", e)
