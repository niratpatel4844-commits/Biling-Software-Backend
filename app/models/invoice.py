from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from app.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=True)
    type = Column(String(20), default="sale")  # sale, credit_note, debit_note
    total_amount = Column(Numeric(14, 2), default=0)
    cgst = Column(Numeric(12, 2), default=0)
    sgst = Column(Numeric(12, 2), default=0)
    igst = Column(Numeric(12, 2), default=0)
    status = Column(String(20), default="generated")
    pdf_url = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
