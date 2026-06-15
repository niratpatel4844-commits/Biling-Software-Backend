from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class CustomerPayment(Base):
    __tablename__ = "customer_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(50), unique=True, nullable=False)
    payment_date = Column(DateTime, server_default=func.now())
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("sales.id"), nullable=True) 
    amount = Column(Numeric(14, 2), nullable=False)
    payment_method = Column(String(50), default="Cash") # Cash, UPI, Card, Bank Transfer, Credit
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
