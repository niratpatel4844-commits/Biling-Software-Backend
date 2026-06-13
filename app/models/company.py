from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    company_code = Column(String(50), nullable=True, unique=True, index=True)
    gst_number = Column(String(20), nullable=True)
    pan_number = Column(String(15), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India")
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    logo = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    currency = Column(String(10), default="INR")
    timezone = Column(String(50), default="Asia/Kolkata")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="company")
    branches = relationship("Branch", back_populates="company")
    franchises = relationship("Franchise", back_populates="company")
    warehouses = relationship("Warehouse", back_populates="company")
