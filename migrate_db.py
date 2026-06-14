from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as con:
        # Vendors
        con.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS payment_terms VARCHAR(100);"))
        
        # Sales
        con.execute(text("ALTER TABLE sales ADD COLUMN IF NOT EXISTS document_type VARCHAR(50) DEFAULT 'invoice';"))
        con.execute(text("ALTER TABLE sales ADD COLUMN IF NOT EXISTS reference_id INTEGER REFERENCES sales(id);"))
        
        # Purchases
        con.execute(text("ALTER TABLE purchases ADD COLUMN IF NOT EXISTS document_type VARCHAR(50) DEFAULT 'purchase_bill';"))
        con.execute(text("ALTER TABLE purchases ADD COLUMN IF NOT EXISTS reference_id INTEGER REFERENCES purchases(id);"))
        
        con.commit()
    print("Database updated successfully with new columns.")
except Exception as e:
    print("Migration failed:", e)
