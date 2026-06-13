from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    gst_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    opening_date = Column(Date, nullable=True)
    country = Column(String(100), default="India")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="branches")
    users = relationship("User", back_populates="branch", foreign_keys="[User.branch_id]")
    inventory = relationship("Inventory", back_populates="branch")
    sales = relationship("Sale", back_populates="branch")
