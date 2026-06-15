from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.company import Company
from app.models.user import User
from app.schemas.schemas import CompanyCreate, CompanyUpdate, CompanyResponse, MessageResponse
from app.utils.auth import require_permission
from app.middleware.audit import create_audit_log
import math

router = APIRouter(prefix="/api/companies", tags=["Company Management"])


@router.get("/", response_model=dict)
def list_companies(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=10000),
    search: str = Query(""),
    user: User = Depends(require_permission("companies", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Company)
    if search:
        q = q.filter(Company.name.ilike(f"%{search}%"))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [CompanyResponse.model_validate(c) for c in items],
            "total": total, "page": page, "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 1}


@router.post("/", response_model=CompanyResponse)
def create_company(data: CompanyCreate, user: User = Depends(require_permission("companies", "create")), db: Session = Depends(get_db)):
    company = Company(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    create_audit_log(db, user.id, "create", "companies", "company", company.id, f"Created company {company.name}")
    return CompanyResponse.model_validate(company)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, user: User = Depends(require_permission("companies", "view")), db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyResponse.model_validate(company)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(company_id: int, data: CompanyUpdate, user: User = Depends(require_permission("companies", "edit")), db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(company, key, val)
    db.commit()
    db.refresh(company)
    return CompanyResponse.model_validate(company)


@router.delete("/{company_id}", response_model=MessageResponse)
def delete_company(company_id: int, user: User = Depends(require_permission("companies", "delete")), db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
    return MessageResponse(message="Company deleted")
