from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.franchise import Franchise
from app.models.user import User
from app.schemas.schemas import FranchiseCreate, FranchiseUpdate, FranchiseResponse, MessageResponse
from app.utils.auth import require_permission
from app.middleware.audit import create_audit_log
import math

router = APIRouter(prefix="/api/franchises", tags=["Franchise Management"])


@router.get("/", response_model=dict)
def list_franchises(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""), status: str = Query(None),
    user: User = Depends(require_permission("franchises", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Franchise)
    if search:
        q = q.filter(Franchise.name.ilike(f"%{search}%"))
    if status:
        q = q.filter(Franchise.status == status)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [FranchiseResponse.model_validate(f) for f in items],
            "total": total, "page": page, "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 1}


@router.post("/", response_model=FranchiseResponse)
def create_franchise(data: FranchiseCreate, user: User = Depends(require_permission("franchises", "create")), db: Session = Depends(get_db)):
    franchise = Franchise(**data.model_dump())
    db.add(franchise)
    db.commit()
    db.refresh(franchise)
    create_audit_log(db, user.id, "create", "franchises", "franchise", franchise.id, f"Created franchise {franchise.name}")
    return FranchiseResponse.model_validate(franchise)


@router.put("/{franchise_id}", response_model=FranchiseResponse)
def update_franchise(franchise_id: int, data: FranchiseUpdate, user: User = Depends(require_permission("franchises", "edit")), db: Session = Depends(get_db)):
    franchise = db.query(Franchise).filter(Franchise.id == franchise_id).first()
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(franchise, key, val)
    db.commit()
    db.refresh(franchise)
    return FranchiseResponse.model_validate(franchise)


@router.post("/{franchise_id}/approve", response_model=MessageResponse)
def approve_franchise(franchise_id: int, user: User = Depends(require_permission("franchises", "approve")), db: Session = Depends(get_db)):
    franchise = db.query(Franchise).filter(Franchise.id == franchise_id).first()
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found")
    franchise.status = "approved"
    franchise.is_active = True
    db.commit()
    return MessageResponse(message="Franchise approved")


@router.post("/{franchise_id}/suspend", response_model=MessageResponse)
def suspend_franchise(franchise_id: int, user: User = Depends(require_permission("franchises", "edit")), db: Session = Depends(get_db)):
    franchise = db.query(Franchise).filter(Franchise.id == franchise_id).first()
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found")
    franchise.status = "suspended"
    franchise.is_active = False
    db.commit()
    return MessageResponse(message="Franchise suspended")
