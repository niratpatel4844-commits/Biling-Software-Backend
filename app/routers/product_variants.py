from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product_variant import ProductVariant
from app.models.product import Product
from app.models.user import User
from app.schemas.schemas import ProductVariantCreate, ProductVariantUpdate, ProductVariantResponse, PaginatedResponse, MessageResponse
from app.utils.auth import require_permission
from sqlalchemy import or_

router = APIRouter(prefix="/api/variants", tags=["Product Variant Management"])

@router.get("/", response_model=PaginatedResponse)
def list_variants(
    product_id: int = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    search: str = "",
    user: User = Depends(require_permission("variants", "view")),
    db: Session = Depends(get_db)
):
    query = db.query(ProductVariant)
    if product_id:
        query = query.filter(ProductVariant.product_id == product_id)
    if search:
        query = query.filter(or_(ProductVariant.name.ilike(f"%{search}%"), ProductVariant.sku.ilike(f"%{search}%")))
    total = query.count()
    items = query.order_by(ProductVariant.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [ProductVariantResponse.model_validate(p) for p in items], "total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size}

@router.post("/", response_model=ProductVariantResponse)
def create_variant(data: ProductVariantCreate, user: User = Depends(require_permission("variants", "create")), db: Session = Depends(get_db)):
    if db.query(ProductVariant).filter(ProductVariant.sku == data.sku).first():
        raise HTTPException(status_code=400, detail="Variant SKU already exists")
    if not db.query(Product).filter(Product.id == data.product_id).first():
        raise HTTPException(status_code=400, detail="Product not found")
    variant = ProductVariant(**data.model_dump())
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant

@router.put("/{variant_id}", response_model=ProductVariantResponse)
def update_variant(variant_id: int, data: ProductVariantUpdate, user: User = Depends(require_permission("variants", "edit")), db: Session = Depends(get_db)):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    if data.sku and data.sku != variant.sku:
        if db.query(ProductVariant).filter(ProductVariant.sku == data.sku).first():
            raise HTTPException(status_code=400, detail="Variant SKU already exists")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(variant, key, val)
    db.commit()
    db.refresh(variant)
    return variant

@router.delete("/{variant_id}", response_model=MessageResponse)
def delete_variant(variant_id: int, user: User = Depends(require_permission("variants", "delete")), db: Session = Depends(get_db)):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    db.delete(variant)
    db.commit()
    return {"message": "Variant deleted", "success": True}
