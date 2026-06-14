from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(50), default="purchase_bill") # purchase_request, purchase_order, goods_receipt, purchase_bill, vendor_return
    po_number = Column(String(50), unique=True, nullable=False)
    reference_id = Column(Integer, ForeignKey("purchases.id"), nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    purchase_date = Column(DateTime, server_default=func.now())
    order_date = Column(DateTime, server_default=func.now())
    expected_date = Column(DateTime, nullable=True)
    received_date = Column(DateTime, nullable=True)
    subtotal = Column(Numeric(14, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(14, 2), default=0)
    paid_amount = Column(Numeric(14, 2), default=0)
    status = Column(String(20), default="pending")
    payment_status = Column(String(20), default="unpaid")
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    vendor = relationship("Vendor", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    received_quantity = Column(Integer, default=0)
    unit_price = Column(Numeric(12, 2), nullable=False)
    gst_percent = Column(Numeric(5, 2), default=0)
    total = Column(Numeric(14, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")
