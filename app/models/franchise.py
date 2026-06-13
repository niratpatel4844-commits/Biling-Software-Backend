from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Franchise(Base):
    __tablename__ = "franchises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    owner_name = Column(String(255), nullable=False)
    owner_email = Column(String(255), nullable=True)
    owner_mobile = Column(String(20), nullable=True)
    agreement_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    commission_percent = Column(Numeric(5, 2), default=0)
    royalty_percent = Column(Numeric(5, 2), default=0)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="India")
    pincode = Column(String(10), nullable=True)
    gst_number = Column(String(20), nullable=True)
    pan_number = Column(String(15), nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, suspended, terminated
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="franchises")
    users = relationship("User", back_populates="franchise")
    inventory = relationship("Inventory", back_populates="franchise")
    sales = relationship("Sale", back_populates="franchise")
