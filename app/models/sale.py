from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(50), default="invoice") # quotation, sales_order, invoice, return, credit_note
    invoice_number = Column(String(50), unique=True, nullable=False)
    reference_id = Column(Integer, ForeignKey("sales.id"), nullable=True) # To link order to invoice etc.
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    franchise_id = Column(Integer, ForeignKey("franchises.id"), nullable=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    sales_person_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sale_date = Column(DateTime, server_default=func.now())
    subtotal = Column(Numeric(14, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    cgst = Column(Numeric(12, 2), default=0)
    sgst = Column(Numeric(12, 2), default=0)
    igst = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(14, 2), default=0)
    paid_amount = Column(Numeric(14, 2), default=0)
    due_amount = Column(Numeric(14, 2), default=0)
    payment_method = Column(String(50), default="cash")
    payment_status = Column(String(20), default="paid")  # paid, partial, unpaid
    status = Column(String(20), default="completed")  # completed, returned, refunded
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="sales")
    branch = relationship("Branch", back_populates="sales")
    franchise = relationship("Franchise", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    gst_percent = Column(Numeric(5, 2), default=0)
    gst_amount = Column(Numeric(12, 2), default=0)
    total = Column(Numeric(14, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
