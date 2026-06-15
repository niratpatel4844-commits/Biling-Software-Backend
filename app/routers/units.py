from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.unit import Unit
from app.models.user import User
from app.schemas.schemas import UnitCreate, UnitUpdate, UnitResponse, PaginatedResponse, MessageResponse
from app.utils.auth import require_permission
from sqlalchemy import or_

router = APIRouter(prefix="/api/units", tags=["Unit Management"])

@router.get("/", response_model=PaginatedResponse)
def list_units(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    search: str = "",
    user: User = Depends(require_permission("units", "view")),
    db: Session = Depends(get_db)
):
    query = db.query(Unit)
    if search:
        query = query.filter(or_(Unit.name.ilike(f"%{search}%"), Unit.code.ilike(f"%{search}%")))
    total = query.count()
    items = query.order_by(Unit.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [UnitResponse.model_validate(p) for p in items], "total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size}

@router.post("/", response_model=UnitResponse)
def create_unit(data: UnitCreate, user: User = Depends(require_permission("units", "create")), db: Session = Depends(get_db)):
    if db.query(Unit).filter(Unit.code == data.code).first():
        raise HTTPException(status_code=400, detail="Unit code already exists")
    unit = Unit(**data.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit

@router.put("/{unit_id}", response_model=UnitResponse)
def update_unit(unit_id: int, data: UnitUpdate, user: User = Depends(require_permission("units", "edit")), db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    if data.code and data.code != unit.code:
        if db.query(Unit).filter(Unit.code == data.code).first():
            raise HTTPException(status_code=400, detail="Unit code already exists")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(unit, key, val)
    db.commit()
    db.refresh(unit)
    return unit

@router.delete("/{unit_id}", response_model=MessageResponse)
def delete_unit(unit_id: int, user: User = Depends(require_permission("units", "delete")), db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    db.delete(unit)
    db.commit()
    return {"message": "Unit deleted", "success": True}
