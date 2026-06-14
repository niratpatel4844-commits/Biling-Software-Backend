from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as con:
        con.execute(text("ALTER TABLE roles ADD COLUMN allow_company BOOLEAN DEFAULT true;"))
        con.execute(text("ALTER TABLE roles ADD COLUMN allow_branch BOOLEAN DEFAULT false;"))
        con.execute(text("ALTER TABLE roles ADD COLUMN allow_franchise BOOLEAN DEFAULT false;"))
        con.execute(text("ALTER TABLE roles ADD COLUMN allow_warehouse BOOLEAN DEFAULT false;"))
        con.commit()
    print("Added assignment configuration columns to roles.")
except Exception as e:
    print("Error:", e)
