from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class VendorPayment(Base):
    __tablename__ = "vendor_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False)
    payment_date = Column(DateTime, server_default=func.now())
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    purchase_bill_id = Column(Integer, ForeignKey("purchases.id"), nullable=True) 
    amount = Column(Numeric(14, 2), nullable=False)
    payment_method = Column(String(50), default="Cash") # Cash, UPI, Card, Bank Transfer, Cheque
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
