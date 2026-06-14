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
    # (name, display, is_system, allow_branch, allow_franchise, allow_warehouse)
    ("super_admin", "Super Admin", True, False, False, False),
    ("admin", "Admin", True, False, False, False),
    ("manager", "Manager", True, True, False, False),
    ("warehouse_manager", "Warehouse Manager", True, False, False, True),
    ("branch_manager", "Branch Manager", True, True, False, False),
    ("franchise_manager", "Franchise Manager", True, False, True, False),
    ("accountant", "Accountant", True, True, False, False),
    ("sales_staff", "Sales Staff", True, True, False, False),
    ("support_staff", "Support Staff", True, False, False, False),
]

MODULES = [
    "dashboard", "products", "categories", "brands", "units", "variants",
    "inventory", "sales", "purchases", "reports", "finance", "users", 
    "settings", "companies", "branches", "franchises", "warehouses", 
    "customers", "vendors",
]

ACTIONS = ["view", "create", "edit", "delete", "approve", "export", "import"]


def seed_default_data():
    db = SessionLocal()
    try:
        for name, display, is_system, allow_branch, allow_franchise, allow_warehouse in SYSTEM_ROLES:
            if not db.query(Role).filter(Role.name == name).first():
                db.add(Role(name=name, display_name=display, is_system=is_system, allow_company=True, allow_branch=allow_branch, allow_franchise=allow_franchise, allow_warehouse=allow_warehouse))
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
