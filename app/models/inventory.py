from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    franchise_id = Column(Integer, ForeignKey("franchises.id"), nullable=True)
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    damaged_quantity = Column(Integer, default=0)
    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    location = Column(String(100), nullable=True)  # rack/shelf location
    last_restocked = Column(DateTime, nullable=True)
    last_stock_check = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="inventory")
    branch = relationship("Branch", back_populates="inventory")
    warehouse = relationship("Warehouse", back_populates="inventory")
    franchise = relationship("Franchise", back_populates="inventory")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    from_type = Column(String(20), nullable=True)  # warehouse, branch, franchise
    from_id = Column(Integer, nullable=True)
    to_type = Column(String(20), nullable=True)
    to_id = Column(Integer, nullable=True)
    quantity = Column(Integer, nullable=False)
    movement_type = Column(String(30), nullable=False)  # transfer, adjustment, return, damage
    reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class StockHistory(Base):
    __tablename__ = "stock_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    transaction_type = Column(String(50), nullable=False)  # OPENING_STOCK, PURCHASE, SALES, etc.
    previous_stock = Column(Integer, default=0)
    quantity_in = Column(Integer, default=0)
    quantity_out = Column(Integer, default=0)
    new_stock = Column(Integer, default=0)
    reference_id = Column(String(100), nullable=True)
    remarks = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
