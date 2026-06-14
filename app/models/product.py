from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    gst_percent = Column(Numeric(5, 2), default=18)
    hsn_code = Column(String(20), nullable=True)
    cost_price = Column(Numeric(12, 2), nullable=False)
    selling_price = Column(Numeric(12, 2), nullable=False)
    mrp = Column(Numeric(12, 2), nullable=True)
    discount_percent = Column(Numeric(5, 2), default=0)
    barcode = Column(String(100), nullable=True)
    qr_code = Column(Text, nullable=True)
    image = Column(Text, nullable=True)
    min_stock = Column(Integer, default=10)
    max_stock = Column(Integer, default=1000)
    reorder_level = Column(Integer, default=20)
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    unit = relationship("Unit", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")
