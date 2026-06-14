from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as con:
        # Create Brands table
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS brands (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                brand_code VARCHAR(100) UNIQUE,
                description TEXT,
                logo TEXT,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        print("Brands table created.")

        # Create Units table
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS units (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        print("Units table created.")

        # Insert some default units just in case
        con.execute(text("INSERT INTO units (name, code) VALUES ('Pieces', 'PCS') ON CONFLICT DO NOTHING;"))
        con.execute(text("INSERT INTO units (name, code) VALUES ('Kilograms', 'KG') ON CONFLICT DO NOTHING;"))

        # Create ProductVariants table
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS product_variants (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                sku VARCHAR(100) UNIQUE NOT NULL,
                color VARCHAR(100),
                size VARCHAR(100),
                weight VARCHAR(100),
                cost_price NUMERIC(12, 2),
                selling_price NUMERIC(12, 2),
                barcode VARCHAR(100),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        print("ProductVariants table created.")

        # Modify products table: Drop old brand/unit columns and add brand_id/unit_id
        try:
            con.execute(text("ALTER TABLE products DROP COLUMN IF EXISTS brand;"))
            con.execute(text("ALTER TABLE products DROP COLUMN IF EXISTS unit;"))
            con.execute(text("ALTER TABLE products ADD COLUMN brand_id INTEGER REFERENCES brands(id);"))
            con.execute(text("ALTER TABLE products ADD COLUMN unit_id INTEGER REFERENCES units(id);"))
            print("Products table updated to use brand_id and unit_id foreign keys.")
        except Exception as e:
            print("Notice on modifying products table:", e)

        con.commit()
    print("Catalog migration completed successfully.")
except Exception as e:
    print("Migration failed:", e)
