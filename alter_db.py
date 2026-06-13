from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as con:
        con.execute(text("ALTER TABLE companies ADD COLUMN company_code VARCHAR(50);"))
        con.execute(text("ALTER TABLE companies ADD CONSTRAINT unique_company_code UNIQUE (company_code);"))
        con.commit()
    print("Added company_code column.")
except Exception as e:
    print("Error:", e)
