from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.role import role_permissions


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String(100), nullable=False)  # e.g., "dashboard", "products"
    action = Column(String(50), nullable=False)    # e.g., "view", "create", "edit", "delete"
    name = Column(String(200), unique=True, nullable=False)  # e.g., "products.create"
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
