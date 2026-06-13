from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.branch import Branch
from app.models.franchise import Franchise
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.sale import Sale
from app.models.purchase import Purchase
from app.models.customer import Customer
from app.models.vendor import Vendor
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.utils.auth import get_current_user
import math

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    today_sales = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(Sale.sale_date >= today_start).scalar()
    monthly_sales = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(Sale.sale_date >= month_start).scalar()
    total_inv_value = db.query(func.coalesce(func.sum(Inventory.quantity * Product.selling_price), 0)).join(Product).scalar()

    low_stock = db.query(func.count(Inventory.id)).filter(Inventory.quantity <= 10, Inventory.quantity > 0).scalar()
    out_of_stock = db.query(func.count(Inventory.id)).filter(Inventory.quantity <= 0).scalar()
    pending_orders = db.query(func.count(Purchase.id)).filter(Purchase.status == "pending").scalar()

    return {
        "total_companies": db.query(func.count(Company.id)).scalar(),
        "total_warehouses": db.query(func.count(Warehouse.id)).scalar(),
        "total_branches": db.query(func.count(Branch.id)).scalar(),
        "total_franchises": db.query(func.count(Franchise.id)).scalar(),
        "total_users": db.query(func.count(User.id)).scalar(),
        "total_products": db.query(func.count(Product.id)).scalar(),
        "total_inventory_value": float(total_inv_value),
        "today_sales": float(today_sales),
        "monthly_sales": float(monthly_sales),
        "pending_orders": pending_orders,
        "low_stock_products": low_stock,
        "out_of_stock_products": out_of_stock,
        "total_customers": db.query(func.count(Customer.id)).scalar(),
        "total_vendors": db.query(func.count(Vendor.id)).scalar(),
    }


@router.get("/sales-trend")
def sales_trend(days: int = Query(30), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    sales = db.query(
        func.date(Sale.sale_date).label("date"),
        func.sum(Sale.total_amount).label("amount")
    ).filter(Sale.sale_date >= start).group_by(func.date(Sale.sale_date)).order_by(func.date(Sale.sale_date)).all()
    return [{"date": str(s.date), "amount": float(s.amount)} for s in sales]


@router.get("/recent-activities")
def recent_activities(limit: int = Query(20), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
    return [{"id": l.id, "action": l.action, "module": l.module, "details": l.details,
             "user_id": l.user_id, "created_at": str(l.created_at)} for l in logs]


@router.get("/notifications")
def get_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(
        (Notification.user_id == user.id) | (Notification.user_id == None)
    ).order_by(desc(Notification.created_at)).limit(20).all()
    return [{"id": n.id, "title": n.title, "message": n.message, "type": n.type,
             "is_read": n.is_read, "created_at": str(n.created_at)} for n in notifs]


@router.get("/top-products")
def top_products(limit: int = Query(10), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.sale import SaleItem
    results = db.query(
        Product.name,
        func.sum(SaleItem.quantity).label("total_qty"),
        func.sum(SaleItem.total).label("total_revenue")
    ).join(SaleItem, SaleItem.product_id == Product.id).group_by(Product.name).order_by(desc("total_qty")).limit(limit).all()
    return [{"name": r.name, "quantity": int(r.total_qty), "revenue": float(r.total_revenue)} for r in results]
