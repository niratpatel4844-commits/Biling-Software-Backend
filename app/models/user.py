from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    mobile = Column(String(20), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    profile_image = Column(Text, nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    franchise_id = Column(Integer, ForeignKey("franchises.id"), nullable=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(50), nullable=True)
    last_login_device = Column(String(255), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    refresh_token = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    role = relationship("Role", back_populates="users")
    company = relationship("Company", back_populates="users")
    branch = relationship("Branch", back_populates="users", foreign_keys=[branch_id])
    franchise = relationship("Franchise", back_populates="users")
    warehouse = relationship("Warehouse", back_populates="users", foreign_keys=[warehouse_id])
    audit_logs = relationship("AuditLog", back_populates="user")
