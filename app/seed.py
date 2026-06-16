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
from app.models.finance import AccountGroup, Account, AccountType
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
ACTIONS = ["view", "create", "edit", "delete", "approve", "export", "import"]

def seed_finance(db):
    groups = [
        ("Current Assets", AccountType.ASSET),
        ("Fixed Assets", AccountType.ASSET),
        ("Current Liabilities", AccountType.LIABILITY),
        ("Long Term Liabilities", AccountType.LIABILITY),
        ("Equity", AccountType.EQUITY),
        ("Revenue", AccountType.REVENUE),
        ("Cost of Goods Sold", AccountType.EXPENSE),
        ("Operating Expenses", AccountType.EXPENSE),
    ]
    
    group_map = {}
    for name, atype in groups:
        g = db.query(AccountGroup).filter(AccountGroup.name == name).first()
        if not g:
            g = AccountGroup(name=name, type=atype)
            db.add(g)
            db.flush()
        group_map[name] = g
        
    db.commit()

    accounts = [
        ("1000", "Cash", "Current Assets"),
        ("1010", "Bank Account", "Current Assets"),
        ("1200", "Accounts Receivable", "Current Assets"),
        ("1300", "Inventory", "Current Assets"),
        ("2000", "Accounts Payable", "Current Liabilities"),
        ("3000", "Owner's Equity", "Equity"),
        ("4000", "Sales Revenue", "Revenue"),
        ("5000", "Cost of Goods Sold", "Cost of Goods Sold"),
        ("6000", "Rent Expense", "Operating Expenses"),
        ("6010", "Salary Expense", "Operating Expenses"),
        ("6020", "Utilities Expense", "Operating Expenses"),
    ]
    
    for code, name, group_name in accounts:
        a = db.query(Account).filter(Account.code == code).first()
        if not a:
            a = Account(code=code, name=name, group_id=group_map[group_name].id)
            db.add(a)
            
    db.commit()
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
        seed_finance(db)
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
