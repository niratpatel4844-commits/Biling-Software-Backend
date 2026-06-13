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
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""), category_id: int = Query(None),
    user: User = Depends(require_permission("products", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Product)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
    if category_id:
        q = q.filter(Product.category_id == category_id)
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
    product = Product(**data.model_dump())
    db.add(product)
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
    for key, val in data.model_dump(exclude_unset=True).items():
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


# --- Categories ---
cat_router = APIRouter(prefix="/api/categories", tags=["Category Management"])


@cat_router.get("/", response_model=list[CategoryResponse])
def list_categories(user: User = Depends(require_permission("products", "view")), db: Session = Depends(get_db)):
    return [CategoryResponse.model_validate(c) for c in db.query(Category).all()]


@cat_router.post("/", response_model=CategoryResponse)
def create_category(data: CategoryCreate, user: User = Depends(require_permission("products", "create")), db: Session = Depends(get_db)):
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return CategoryResponse.model_validate(cat)


@cat_router.delete("/{cat_id}", response_model=MessageResponse)
def delete_category(cat_id: int, user: User = Depends(require_permission("products", "delete")), db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return MessageResponse(message="Category deleted")
