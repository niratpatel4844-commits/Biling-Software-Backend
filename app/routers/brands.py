from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.brand import Brand
from app.models.user import User
from app.schemas.schemas import BrandCreate, BrandUpdate, BrandResponse, PaginatedResponse, MessageResponse
from app.utils.auth import require_permission
from sqlalchemy import or_

router = APIRouter(prefix="/api/brands", tags=["Brand Management"])

@router.get("/", response_model=PaginatedResponse)
def list_brands(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    search: str = "",
    user: User = Depends(require_permission("brands", "view")),
    db: Session = Depends(get_db)
):
    query = db.query(Brand)
    if search:
        query = query.filter(or_(Brand.name.ilike(f"%{search}%"), Brand.brand_code.ilike(f"%{search}%")))
    total = query.count()
    items = query.order_by(Brand.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [BrandResponse.model_validate(p) for p in items], "total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size}

@router.post("/", response_model=BrandResponse)
def create_brand(data: BrandCreate, user: User = Depends(require_permission("brands", "create")), db: Session = Depends(get_db)):
    if data.brand_code and db.query(Brand).filter(Brand.brand_code == data.brand_code).first():
        raise HTTPException(status_code=400, detail="Brand code already exists")
    brand = Brand(**data.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(brand_id: int, data: BrandUpdate, user: User = Depends(require_permission("brands", "edit")), db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    if data.brand_code and data.brand_code != brand.brand_code:
        if db.query(Brand).filter(Brand.brand_code == data.brand_code).first():
            raise HTTPException(status_code=400, detail="Brand code already exists")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(brand, key, val)
    db.commit()
    db.refresh(brand)
    return brand

@router.delete("/{brand_id}", response_model=MessageResponse)
def delete_brand(brand_id: int, user: User = Depends(require_permission("brands", "delete")), db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    db.delete(brand)
    db.commit()
    return {"message": "Brand deleted", "success": True}
