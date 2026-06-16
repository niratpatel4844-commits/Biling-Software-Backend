from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.setting import Setting
from app.schemas.schemas import SettingCreate, SettingUpdate, SettingResponse
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("/", response_model=List[SettingResponse])
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    settings = db.query(Setting).all()
    return settings

@router.get("/{key}", response_model=SettingResponse)
def get_setting(key: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return setting

@router.put("/{key}", response_model=SettingResponse)
def update_setting(key: str, setting_update: SettingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    setting = db.query(Setting).filter(Setting.key == key).first()
    
    if not setting:
        # If setting doesn't exist, create it if value is provided
        if setting_update.value is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create setting without a value")
            
        setting = Setting(
            key=key, 
            value=setting_update.value,
            group=setting_update.group or "general",
            description=setting_update.description
        )
        db.add(setting)
    else:
        # Update existing
        if setting_update.value is not None:
            setting.value = setting_update.value
        if setting_update.group is not None:
            setting.group = setting_update.group
        if setting_update.description is not None:
            setting.description = setting_update.description
            
    db.commit()
    db.refresh(setting)
    return setting
