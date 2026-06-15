from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class DeliveryChallan(Base):
    __tablename__ = "delivery_challans"
    
    id = Column(Integer, primary_key=True, index=True)
    challan_number = Column(String(50), unique=True, nullable=False)
    date = Column(DateTime, server_default=func.now())
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_order_id = Column(Integer, ForeignKey("sales.id"), nullable=True) 
    delivery_address = Column(Text, nullable=True)
    vehicle_details = Column(String(100), nullable=True)
    driver_name = Column(String(100), nullable=True)
    status = Column(String(20), default="Pending") # Pending, In Transit, Delivered
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    
    items = relationship("DeliveryChallanItem", back_populates="challan", cascade="all, delete-orphan")

class DeliveryChallanItem(Base):
    __tablename__ = "delivery_challan_items"
    
    id = Column(Integer, primary_key=True, index=True)
    challan_id = Column(Integer, ForeignKey("delivery_challans.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    
    challan = relationship("DeliveryChallan", back_populates="items")
