from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")
    channel = Column(String(20), default="in_app")
    user_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False)
    event = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
