"""Seed default data: roles, permissions, and super admin user."""
from app.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.company import Company
from app.models.branch import Branch
from app.models.franchise import Franchise
from app.models.warehouse import Warehouse
from app.models.audit_log import AuditLog
from app.utils.auth import hash_password


SYSTEM_ROLES = [
    ("super_admin", "Super Admin", True),
    ("admin", "Admin", True),
    ("manager", "Manager", True),
    ("warehouse_manager", "Warehouse Manager", True),
    ("branch_manager", "Branch Manager", True),
    ("franchise_manager", "Franchise Manager", True),
    ("accountant", "Accountant", True),
    ("sales_staff", "Sales Staff", True),
    ("support_staff", "Support Staff", True),
]

MODULES = [
    "dashboard", "products", "inventory", "sales", "purchases",
    "reports", "finance", "users", "settings", "companies",
    "branches", "franchises", "warehouses", "customers", "vendors",
]

ACTIONS = ["view", "create", "edit", "delete", "approve", "export", "import"]


def seed_default_data():
    db = SessionLocal()
    try:
        # Seed roles
        for name, display, is_system in SYSTEM_ROLES:
            if not db.query(Role).filter(Role.name == name).first():
                db.add(Role(name=name, display_name=display, is_system=is_system))
        db.commit()

        # Seed permissions
        for module in MODULES:
            for action in ACTIONS:
                perm_name = f"{module}.{action}"
                if not db.query(Permission).filter(Permission.name == perm_name).first():
                    db.add(Permission(
                        module=module, action=action, name=perm_name,
                        display_name=f"{action.title()} {module.replace('_', ' ').title()}"
                    ))
        db.commit()

        # Assign all permissions to super_admin role
        sa_role = db.query(Role).filter(Role.name == "super_admin").first()
        if sa_role:
            all_perms = db.query(Permission).all()
            sa_role.permissions = all_perms
            db.commit()

        # Seed super admin user
        if not db.query(User).filter(User.email == "admin@erp.com").first():
            sa_role = db.query(Role).filter(Role.name == "super_admin").first()
            admin = User(
                full_name="Super Admin",
                email="admin@erp.com",
                mobile="9999999999",
                password_hash=hash_password("Admin@123"),
                role_id=sa_role.id if sa_role else None,
                is_superadmin=True,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("✅ Super Admin created: admin@erp.com / Admin@123")
    finally:
        db.close()
