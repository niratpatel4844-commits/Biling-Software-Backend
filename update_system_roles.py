from app.database import SessionLocal
from app.models.role import Role

db = SessionLocal()
try:
    # Set proper defaults for existing system roles
    db.query(Role).filter(Role.name == "manager").update({"allow_branch": True})
    db.query(Role).filter(Role.name == "warehouse_manager").update({"allow_warehouse": True})
    db.query(Role).filter(Role.name == "branch_manager").update({"allow_branch": True})
    db.query(Role).filter(Role.name == "franchise_manager").update({"allow_franchise": True})
    db.query(Role).filter(Role.name == "sales_staff").update({"allow_branch": True})
    db.query(Role).filter(Role.name == "accountant").update({"allow_branch": True})
    db.commit()
    print("Successfully updated existing system roles with correct assignment configurations!")
except Exception as e:
    print("Error:", e)
finally:
    db.close()
