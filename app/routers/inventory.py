from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import User
from app.schemas.schemas import InventoryResponse
from app.utils.auth import require_permission
import math

router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])

@router.get("/", response_model=dict)
def list_inventory(
    page: int = Query(1, ge=1), 
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    user: User = Depends(require_permission("inventory", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Inventory, Product).join(Product, Inventory.product_id == Product.id)
    
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
        
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for inv, prod in items:
        inv_data = InventoryResponse.model_validate(inv).model_dump()
        inv_data["product_name"] = prod.name
        inv_data["product_sku"] = prod.sku
        result.append(inv_data)
        
    return {
        "items": result,
        "total": total, 
        "page": page, 
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 1
    }
