from app.database import SessionLocal
from app.models.user import User
from app.utils.auth import hash_password

db = SessionLocal()
try:
    users = db.query(User).all()
    for user in users:
        print(f"User: {user.email}")
        user.password_hash = hash_password("Admin@123")
        user.failed_login_attempts = 0
        user.is_locked = False
        user.is_active = True
    db.commit()
    print("Reset all passwords to Admin@123 and unlocked all accounts.")
finally:
    db.close()
