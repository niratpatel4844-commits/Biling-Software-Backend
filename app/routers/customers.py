from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.customer import Customer
from app.models.vendor import Vendor
from app.models.user import User
from app.schemas.schemas import CustomerCreate, CustomerResponse, VendorCreate, VendorResponse, MessageResponse
from app.utils.auth import require_permission
import math

router = APIRouter(prefix="/api/customers", tags=["Customer Management"])


@router.get("/", response_model=dict)
def list_customers(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    user: User = Depends(require_permission("customers", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Customer)
    if search:
        q = q.filter(Customer.name.ilike(f"%{search}%"))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [CustomerResponse.model_validate(c) for c in items],
            "total": total, "page": page, "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 1}


@router.post("/", response_model=CustomerResponse)
def create_customer(data: CustomerCreate, user: User = Depends(require_permission("customers", "create")), db: Session = Depends(get_db)):
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.delete("/{cust_id}", response_model=MessageResponse)
def delete_customer(cust_id: int, user: User = Depends(require_permission("customers", "delete")), db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == cust_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(cust)
    db.commit()
    return MessageResponse(message="Customer deleted")


# --- Vendors ---
vendor_router = APIRouter(prefix="/api/vendors", tags=["Vendor Management"])


@vendor_router.get("/", response_model=dict)
def list_vendors(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    user: User = Depends(require_permission("vendors", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Vendor)
    if search:
        q = q.filter(Vendor.name.ilike(f"%{search}%"))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [VendorResponse.model_validate(v) for v in items],
            "total": total, "page": page, "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 1}


@vendor_router.post("/", response_model=VendorResponse)
def create_vendor(data: VendorCreate, user: User = Depends(require_permission("vendors", "create")), db: Session = Depends(get_db)):
    vendor = Vendor(**data.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return VendorResponse.model_validate(vendor)


@vendor_router.delete("/{vendor_id}", response_model=MessageResponse)
def delete_vendor(vendor_id: int, user: User = Depends(require_permission("vendors", "delete")), db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.delete(vendor)
    db.commit()
    return MessageResponse(message="Vendor deleted")
