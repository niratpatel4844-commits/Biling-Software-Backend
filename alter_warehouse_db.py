from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as con:
        con.execute(text("ALTER TABLE warehouses ADD COLUMN email VARCHAR(255);"))
        con.commit()
    print("Added email column to warehouses.")
except Exception as e:
    print("Error adding email:", e)

try:
    with engine.connect() as con:
        con.execute(text("ALTER TABLE warehouses ADD COLUMN pincode VARCHAR(10);"))
        con.commit()
    print("Added pincode column to warehouses.")
except Exception as e:
    print("Error adding pincode:", e)

