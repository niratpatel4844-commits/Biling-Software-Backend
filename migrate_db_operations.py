import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://biling_software_user:fDQK3FqMatn4wqbKU3y0hInbe5irRWf3@dpg-d8mkrh3bc2fs73e3n5u0-a.singapore-postgres.render.com/biling_software"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as con:
        # Customers
        con.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS customer_code VARCHAR(50) UNIQUE;"))
        con.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS contact_person VARCHAR(255);"))
        con.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'India';"))
        con.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS pan_number VARCHAR(20);"))
        con.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS notes TEXT;"))

        # Vendors
        con.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS vendor_code VARCHAR(50) UNIQUE;"))
        con.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS contact_person VARCHAR(255);"))
        con.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'India';"))
        con.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS pincode VARCHAR(10);"))
        con.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS notes TEXT;"))

        # Sales
        con.execute(text("ALTER TABLE sales ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id);"))
        con.execute(text("ALTER TABLE sales ADD COLUMN IF NOT EXISTS warehouse_id INTEGER REFERENCES warehouses(id);"))
        con.execute(text("ALTER TABLE sales ADD COLUMN IF NOT EXISTS sales_person_id INTEGER REFERENCES users(id);"))

        # Sale Items
        con.execute(text("ALTER TABLE sale_items ADD COLUMN IF NOT EXISTS product_variant_id INTEGER REFERENCES product_variants(id);"))
        con.execute(text("ALTER TABLE sale_items ADD COLUMN IF NOT EXISTS unit_id INTEGER REFERENCES units(id);"))

        # Purchases
        con.execute(text("ALTER TABLE purchases ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id);"))
        con.execute(text("ALTER TABLE purchases ADD COLUMN IF NOT EXISTS purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
        con.execute(text("ALTER TABLE purchases ADD COLUMN IF NOT EXISTS discount_amount NUMERIC(12, 2) DEFAULT 0;"))

        # Purchase Items
        con.execute(text("ALTER TABLE purchase_items ADD COLUMN IF NOT EXISTS product_variant_id INTEGER REFERENCES product_variants(id);"))
        con.execute(text("ALTER TABLE purchase_items ADD COLUMN IF NOT EXISTS unit_id INTEGER REFERENCES units(id);"))

        con.commit()
    print("Database updated successfully with new operations columns.")
except Exception as e:
    print("Migration failed:", e)
