from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=20, max_overflow=30)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import (
        user, role, permission, company, branch, franchise,
        warehouse, product, category, inventory, sale, purchase,
        customer, vendor, invoice, audit_log, notification, setting,
        delivery_challan, customer_payment
    )
    Base.metadata.create_all(bind=engine)
