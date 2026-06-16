from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.notification import Notification
from app.schemas.schemas import NotificationResponse, NotificationUpdate, PaginatedResponse
from app.routers.auth import get_current_user
from app.models.user import User
import math

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("/", response_model=PaginatedResponse)
def get_notifications(
    page: int = 1,
    page_size: int = 50,
    is_read: bool = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    query = db.query(Notification).filter(
        (Notification.user_id == current_user.id) | (Notification.user_id == None)
    )
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
        
    query = query.order_by(Notification.created_at.desc())
    
    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    notifications = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Convert to pydantic models to match PaginatedResponse expectation
    items = []
    for n in notifications:
        items.append({
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at
        })
        
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        (Notification.user_id == current_user.id) | (Notification.user_id == None)
    ).first()
    
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification

@router.put("/read-all", status_code=status.HTTP_200_OK)
def mark_all_as_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter(
        (Notification.user_id == current_user.id) | (Notification.user_id == None),
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}
