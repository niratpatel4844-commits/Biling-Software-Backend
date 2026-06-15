from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, PaginatedResponse, MessageResponse
from app.utils.auth import require_permission
from sqlalchemy import or_

router = APIRouter(prefix="/api/categories", tags=["Category Management"])

@router.get("/", response_model=PaginatedResponse)
def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    search: str = "",
    parent_id: int = Query(None),
    level: int = Query(None),
    user: User = Depends(require_permission("categories", "view")),
    db: Session = Depends(get_db)
):
    query = db.query(Category)
    if search:
        query = query.filter(or_(Category.name.ilike(f"%{search}%"), Category.category_code.ilike(f"%{search}%")))
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    if level is not None:
        query = query.filter(Category.level == level)
    
    total = query.count()
    items = query.order_by(Category.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [CategoryResponse.model_validate(p) for p in items], "total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size}

@router.post("/", response_model=CategoryResponse)
def create_category(data: CategoryCreate, user: User = Depends(require_permission("categories", "create")), db: Session = Depends(get_db)):
    if data.slug and db.query(Category).filter(Category.slug == data.slug).first():
        raise HTTPException(status_code=400, detail="Category slug already exists")
    if not data.slug:
        data.slug = data.name.lower().replace(" ", "-")
        # Ensure unique
        count = 1
        base_slug = data.slug
        while db.query(Category).filter(Category.slug == data.slug).first():
            data.slug = f"{base_slug}-{count}"
            count += 1
            
    if data.category_code and db.query(Category).filter(Category.category_code == data.category_code).first():
        raise HTTPException(status_code=400, detail="Category code already exists")
        
    if data.level == 1 and data.main_category_id:
        data.parent_id = data.main_category_id
        
    payload = data.model_dump(exclude={"main_category_id"})
    category = Category(**payload)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryUpdate, user: User = Depends(require_permission("categories", "edit")), db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    if data.slug and data.slug != category.slug:
        if db.query(Category).filter(Category.slug == data.slug).first():
            raise HTTPException(status_code=400, detail="Category slug already exists")
            
    if data.category_code and data.category_code != category.category_code:
        if db.query(Category).filter(Category.category_code == data.category_code).first():
            raise HTTPException(status_code=400, detail="Category code already exists")

    if data.level == 1 and data.main_category_id:
        data.parent_id = data.main_category_id

    for key, val in data.model_dump(exclude_unset=True, exclude={"main_category_id"}).items():
        setattr(category, key, val)
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}", response_model=MessageResponse)
def delete_category(category_id: int, user: User = Depends(require_permission("categories", "delete")), db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if has children
    if db.query(Category).filter(Category.parent_id == category_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete category because it has subcategories")
        
    db.delete(category)
    db.commit()
    return {"message": "Category deleted", "success": True}
