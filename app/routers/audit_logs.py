from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.schemas import AuditLogResponse
from app.utils.auth import require_superadmin
import math

router = APIRouter(prefix="/api/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=dict)
def list_audit_logs(
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
    search: str = Query(""), action: str = Query(None), module: str = Query(None),
    user_id: int = Query(None),
    user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    q = db.query(AuditLog)
    if search:
        q = q.filter(AuditLog.action.ilike(f"%{search}%") | AuditLog.module.ilike(f"%{search}%") | AuditLog.details.ilike(f"%{search}%"))
    if action:
        q = q.filter(AuditLog.action == action)
    if module:
        q = q.filter(AuditLog.module == module)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    total = q.count()
    items = q.order_by(desc(AuditLog.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [AuditLogResponse.model_validate(l) for l in items],
            "total": total, "page": page, "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 1}
