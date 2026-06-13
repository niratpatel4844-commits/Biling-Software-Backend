from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User
from app.schemas.schemas import LoginRequest, TokenResponse, RefreshTokenRequest, UserResponse, MessageResponse
from app.utils.auth import (
    verify_password, create_access_token, create_refresh_token,
    decode_token, get_current_user, hash_password
)
from app.middleware.audit import create_audit_log

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= 5:
                user.is_locked = True
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")
    if user.is_locked:
        raise HTTPException(status_code=403, detail="Account locked")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user.refresh_token = refresh_token
    user.last_login = datetime.now(timezone.utc)
    user.last_login_ip = request.client.host if request.client else None
    user.last_login_device = request.headers.get("user-agent", "")
    user.failed_login_attempts = 0
    db.commit()

    create_audit_log(db, user.id, "login", "auth", "user", user.id,
                     "User logged in", request.client.host if request.client else "")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or user.refresh_token != req.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})
    user.refresh_token = new_refresh
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.refresh_token = None
    db.commit()
    create_audit_log(db, user.id, "logout", "auth", "user", user.id, "User logged out",
                     request.client.host if request.client else "")
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
