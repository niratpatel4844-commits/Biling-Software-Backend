from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int = None,
    action: str = "",
    module: str = "",
    entity_type: str = "",
    entity_id: int = None,
    details: str = "",
    ip_address: str = "",
    device: str = "",
    user_agent: str = ""
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
        device=device,
        user_agent=user_agent,
    )
    db.add(log)
    db.commit()
    return log
