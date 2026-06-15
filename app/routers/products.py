from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.schemas.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryResponse, MessageResponse
)
from app.utils.auth import require_permission
import math

router = APIRouter(prefix="/api/products", tags=["Product Management"])


@router.get("/", response_model=dict)
def list_products(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=10000),
    search: str = Query(""), category_id: int = Query(None),
    user: User = Depends(require_permission("products", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Product)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
    if category_id:
        q = q.filter(Product.category_id == category_id)
    q = q.order_by(Product.id.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [ProductResponse.model_validate(p) for p in items],
            "total": total, "page": page, "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 1}


@router.post("/", response_model=ProductResponse)
def create_product(data: ProductCreate, user: User = Depends(require_permission("products", "create")), db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.sku == data.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
        
    actual_category_id = data.child_category_id or data.sub_category_id or data.category_id
    payload = data.model_dump(exclude={"sub_category_id", "child_category_id", "category_id"})
    payload["category_id"] = actual_category_id
    
    product = Product(**payload)
    db.add(product)
    db.flush() # flush to get product id
    
    # Automatically initialize inventory record as requested
    from app.models.inventory import Inventory
    initial_inventory = Inventory(product_id=product.id, quantity=0)
    db.add(initial_inventory)
    
    db.commit()
    db.refresh(product)
    return ProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, user: User = Depends(require_permission("products", "view")), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, user: User = Depends(require_permission("products", "edit")), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    payload = data.model_dump(exclude_unset=True)
    
    if "child_category_id" in payload or "sub_category_id" in payload or "category_id" in payload:
        actual_category_id = payload.get("child_category_id") or payload.get("sub_category_id") or payload.get("category_id")
        if actual_category_id:
            payload["category_id"] = actual_category_id
            
    payload.pop("child_category_id", None)
    payload.pop("sub_category_id", None)
    
    for key, val in payload.items():
        setattr(product, key, val)
        
    db.commit()
    db.refresh(product)
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", response_model=MessageResponse)
def delete_product(product_id: int, user: User = Depends(require_permission("products", "delete")), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return MessageResponse(message="Product deleted")



