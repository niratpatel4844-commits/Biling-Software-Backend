from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.branch import Branch
from app.models.user import User
from app.schemas.schemas import BranchCreate, BranchUpdate, BranchResponse, MessageResponse
from app.utils.auth import require_permission
from app.middleware.audit import create_audit_log
import math

router = APIRouter(prefix="/api/branches", tags=["Branch Management"])


@router.get("/", response_model=dict)
def list_branches(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""), company_id: int = Query(None),
    user: User = Depends(require_permission("branches", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Branch)
    if search:
        q = q.filter(Branch.name.ilike(f"%{search}%"))
    if company_id:
        q = q.filter(Branch.company_id == company_id)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [BranchResponse.model_validate(b) for b in items],
            "total": total, "page": page, "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 1}


@router.post("/", response_model=BranchResponse)
def create_branch(data: BranchCreate, user: User = Depends(require_permission("branches", "create")), db: Session = Depends(get_db)):
    existing = db.query(Branch).filter(Branch.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Branch code already exists")
    branch = Branch(**data.model_dump())
    db.add(branch)
    db.commit()
    db.refresh(branch)
    create_audit_log(db, user.id, "create", "branches", "branch", branch.id, f"Created branch {branch.name}")
    return BranchResponse.model_validate(branch)


@router.get("/{branch_id}", response_model=BranchResponse)
def get_branch(branch_id: int, user: User = Depends(require_permission("branches", "view")), db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return BranchResponse.model_validate(branch)


@router.put("/{branch_id}", response_model=BranchResponse)
def update_branch(branch_id: int, data: BranchUpdate, user: User = Depends(require_permission("branches", "edit")), db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(branch, key, val)
    db.commit()
    db.refresh(branch)
    return BranchResponse.model_validate(branch)


@router.delete("/{branch_id}", response_model=MessageResponse)
def delete_branch(branch_id: int, user: User = Depends(require_permission("branches", "delete")), db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    db.delete(branch)
    db.commit()
    return MessageResponse(message="Branch deleted")
