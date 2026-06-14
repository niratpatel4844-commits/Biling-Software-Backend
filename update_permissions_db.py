from app.database import SessionLocal
from app.models.permission import Permission
from app.models.role import Role

db = SessionLocal()
try:
    MODULES = ["categories", "brands", "units", "variants"]
    ACTIONS = ["view", "create", "edit", "delete", "approve", "export", "import"]
    
    for module in MODULES:
        for action in ACTIONS:
            perm_name = f"{module}.{action}"
            if not db.query(Permission).filter(Permission.name == perm_name).first():
                db.add(Permission(
                    module=module, action=action, name=perm_name,
                    display_name=f"{action.title()} {module.replace('_', ' ').title()}"
                ))
    db.commit()

    sa_role = db.query(Role).filter(Role.name == "super_admin").first()
    if sa_role:
        all_perms = db.query(Permission).all()
        sa_role.permissions = all_perms
        db.commit()
    print("Permissions for catalog modules updated.")
finally:
    db.close()
