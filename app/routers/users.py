from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.schemas import UserCreate, UserUpdate, UserResponse, MessageResponse, UserResetPassword
from app.utils.auth import get_current_user, require_permission, hash_password
from app.middleware.audit import create_audit_log
import math

router = APIRouter(prefix="/api/users", tags=["User Management"])


@router.get("/", response_model=dict)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=100),
    role_id: int = Query(None),
    is_active: bool = Query(None),
    user: User = Depends(require_permission("users", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(User)
    if search:
        q = q.filter(User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%") | User.mobile.ilike(f"%{search}%"))
    if role_id is not None:
        q = q.filter(User.role_id == role_id)
    if is_active is not None:
        q = q.filter(User.is_active == is_active)
    total = q.count()
    users = q.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [UserResponse.model_validate(u) for u in users],
        "total": total, "page": page, "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 1
    }


@router.post("/", response_model=UserResponse)
def create_user(
    data: UserCreate,
    user: User = Depends(require_permission("users", "create")),
    db: Session = Depends(get_db)
):
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if data.mobile:
        existing_mobile = db.query(User).filter(User.mobile == data.mobile).first()
        if existing_mobile:
            raise HTTPException(status_code=400, detail="Mobile number already registered")
    new_user = User(
        full_name=data.full_name, email=data.email, mobile=data.mobile,
        password_hash=hash_password(data.password),
        role_id=data.role_id, department=data.department, designation=data.designation,
        company_id=data.company_id, branch_id=data.branch_id,
        franchise_id=data.franchise_id, warehouse_id=data.warehouse_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    create_audit_log(db, user.id, "create", "users", "user", new_user.id, f"Created user {new_user.email}")
    return UserResponse.model_validate(new_user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, user: User = Depends(require_permission("users", "view")), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(target)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, data: UserUpdate,
    user: User = Depends(require_permission("users", "edit")),
    db: Session = Depends(get_db)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
        
    if data.email is not None and data.email != target.email:
        existing_email = db.query(User).filter(User.email == data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
            
    if data.mobile is not None and data.mobile != target.mobile:
        existing_mobile = db.query(User).filter(User.mobile == data.mobile).first()
        if existing_mobile:
            raise HTTPException(status_code=400, detail="Mobile number already registered")

    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(target, key, val)
    db.commit()
    db.refresh(target)
    create_audit_log(db, user.id, "update", "users", "user", user_id, f"Updated user {target.email}")
    return UserResponse.model_validate(target)


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int, user: User = Depends(require_permission("users", "delete")), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(target)
    db.commit()
    create_audit_log(db, user.id, "delete", "users", "user", user_id, f"Deleted user {target.email}")
    return MessageResponse(message="User deleted")


@router.post("/{user_id}/reset-password", response_model=MessageResponse)
def reset_password(user_id: int, payload: UserResetPassword, user: User = Depends(require_permission("users", "edit")), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.password_hash = hash_password(payload.password)
    target.is_locked = False
    target.failed_login_attempts = 0
    db.commit()
    return MessageResponse(message="Password reset successfully")


@router.post("/{user_id}/force-logout", response_model=MessageResponse)
def force_logout(user_id: int, user: User = Depends(require_permission("users", "edit")), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.refresh_token = None
    db.commit()
    return MessageResponse(message="User session terminated")
