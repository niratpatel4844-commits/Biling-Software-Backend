from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.schemas.schemas import (
    RoleCreate, RoleUpdate, RoleResponse,
    PermissionCreate, PermissionResponse,
    RolePermissionAssign, MessageResponse
)
from app.utils.auth import require_superadmin, require_permission
from app.middleware.audit import create_audit_log

router = APIRouter(prefix="/api/roles", tags=["Role & Permission Management"])


@router.get("/", response_model=list[RoleResponse])
def list_roles(user: User = Depends(require_permission("users", "view")), db: Session = Depends(get_db)):
    return [RoleResponse.model_validate(r) for r in db.query(Role).all()]


@router.post("/", response_model=RoleResponse)
def create_role(data: RoleCreate, user: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    existing = db.query(Role).filter(Role.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")
    role = Role(name=data.name, display_name=data.display_name, description=data.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    create_audit_log(db, user.id, "create", "roles", "role", role.id, f"Created role {role.name}")
    return RoleResponse.model_validate(role)


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, data: RoleUpdate, user: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot modify system role")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(role, key, val)
    db.commit()
    db.refresh(role)
    return RoleResponse.model_validate(role)


@router.delete("/{role_id}", response_model=MessageResponse)
def delete_role(role_id: int, user: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system role")
    db.delete(role)
    db.commit()
    return MessageResponse(message="Role deleted")


# --- Permissions ---
@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(user: User = Depends(require_permission("users", "view")), db: Session = Depends(get_db)):
    return [PermissionResponse.model_validate(p) for p in db.query(Permission).all()]


@router.post("/permissions", response_model=PermissionResponse)
def create_permission(data: PermissionCreate, user: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    perm = Permission(**data.model_dump())
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return PermissionResponse.model_validate(perm)


@router.post("/{role_id}/permissions", response_model=MessageResponse)
def assign_permissions(role_id: int, data: RolePermissionAssign, user: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    perms = db.query(Permission).filter(Permission.id.in_(data.permission_ids)).all()
    role.permissions = perms
    db.commit()
    create_audit_log(db, user.id, "update", "roles", "role", role_id, f"Updated permissions for {role.name}")
    return MessageResponse(message="Permissions updated")
