from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.warehouse import Warehouse
from app.models.user import User
from app.schemas.schemas import WarehouseCreate, WarehouseUpdate, WarehouseResponse, MessageResponse
from app.utils.auth import require_permission
import math

router = APIRouter(prefix="/api/warehouses", tags=["Warehouse Management"])


@router.get("/", response_model=dict)
def list_warehouses(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    user: User = Depends(require_permission("warehouses", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Warehouse)
    if search:
        q = q.filter(Warehouse.name.ilike(f"%{search}%"))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [WarehouseResponse.model_validate(w) for w in items],
            "total": total, "page": page, "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 1}


@router.post("/", response_model=WarehouseResponse)
def create_warehouse(data: WarehouseCreate, user: User = Depends(require_permission("warehouses", "create")), db: Session = Depends(get_db)):
    warehouse = Warehouse(**data.model_dump())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return WarehouseResponse.model_validate(warehouse)


@router.put("/{wh_id}", response_model=WarehouseResponse)
def update_warehouse(wh_id: int, data: WarehouseUpdate, user: User = Depends(require_permission("warehouses", "edit")), db: Session = Depends(get_db)):
    wh = db.query(Warehouse).filter(Warehouse.id == wh_id).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(wh, key, val)
    db.commit()
    db.refresh(wh)
    return WarehouseResponse.model_validate(wh)


@router.delete("/{wh_id}", response_model=MessageResponse)
def delete_warehouse(wh_id: int, user: User = Depends(require_permission("warehouses", "delete")), db: Session = Depends(get_db)):
    wh = db.query(Warehouse).filter(Warehouse.id == wh_id).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    db.delete(wh)
    db.commit()
    return MessageResponse(message="Warehouse deleted")
