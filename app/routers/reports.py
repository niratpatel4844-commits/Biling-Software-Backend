from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.sale import Sale, SaleItem
from app.models.purchase import Purchase, PurchaseItem
from app.models.customer import Customer
from app.models.vendor import Vendor
from app.models.inventory import Inventory, StockMovement
from app.models.product import Product
from app.utils.auth import require_permission

router = APIRouter(prefix="/api/reports", tags=["Reports"])

def get_date_range(days: int = 30):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

@router.get("/sales", response_model=dict)
def sales_report(days: int = Query(30, ge=1, le=365), user: User = Depends(require_permission("reports", "view")), db: Session = Depends(get_db)):
    start_date, end_date = get_date_range(days)
    
    # Base query
    q = db.query(Sale).filter(Sale.sale_date >= start_date, Sale.status != 'Cancelled')
    
    total_revenue = db.query(func.sum(Sale.total_amount)).filter(Sale.sale_date >= start_date, Sale.status != 'Cancelled').scalar() or 0
    total_orders = q.count()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    total_tax = db.query(func.sum(Sale.tax_amount)).filter(Sale.sale_date >= start_date, Sale.status != 'Cancelled').scalar() or 0
    
    # Trend (Daily)
    trend_query = db.query(
        func.date(Sale.sale_date).label('date'),
        func.sum(Sale.total_amount).label('revenue')
    ).filter(Sale.sale_date >= start_date, Sale.status != 'Cancelled').group_by(func.date(Sale.sale_date)).order_by(func.date(Sale.sale_date)).all()
    
    trend = [{"date": str(r[0]), "revenue": float(r[1] or 0)} for r in trend_query]

    # Top Products
    top_products_q = db.query(
        Product.name,
        func.sum(SaleItem.quantity).label('qty_sold'),
        func.sum(SaleItem.total).label('revenue')
    ).join(SaleItem, Product.id == SaleItem.product_id).join(Sale, SaleItem.sale_id == Sale.id)\
    .filter(Sale.sale_date >= start_date, Sale.status != 'Cancelled')\
    .group_by(Product.name).order_by(desc('qty_sold')).limit(10).all()
    
    top_products = [{"name": r[0], "quantity": int(r[1] or 0), "revenue": float(r[2] or 0)} for r in top_products_q]

    return {
        "summary": {
            "total_revenue": float(total_revenue),
            "total_orders": total_orders,
            "avg_order_value": float(avg_order_value),
            "total_tax": float(total_tax)
        },
        "trend": trend,
        "top_products": top_products
    }

@router.get("/purchases", response_model=dict)
def purchases_report(days: int = Query(30, ge=1, le=365), user: User = Depends(require_permission("reports", "view")), db: Session = Depends(get_db)):
    start_date, end_date = get_date_range(days)
    
    # Base query
    q = db.query(Purchase).filter(Purchase.purchase_date >= start_date, Purchase.status != 'Cancelled')
    
    total_expense = db.query(func.sum(Purchase.total_amount)).filter(Purchase.purchase_date >= start_date, Purchase.status != 'Cancelled').scalar() or 0
    total_orders = q.count()
    avg_order_value = total_expense / total_orders if total_orders > 0 else 0
    
    # Trend (Daily)
    trend_query = db.query(
        func.date(Purchase.purchase_date).label('date'),
        func.sum(Purchase.total_amount).label('expense')
    ).filter(Purchase.purchase_date >= start_date, Purchase.status != 'Cancelled').group_by(func.date(Purchase.purchase_date)).order_by(func.date(Purchase.purchase_date)).all()
    
    trend = [{"date": str(r[0]), "expense": float(r[1] or 0)} for r in trend_query]

    # Top Vendors
    top_vendors_q = db.query(
        Vendor.name,
        func.count(Purchase.id).label('orders'),
        func.sum(Purchase.total_amount).label('total_spent')
    ).join(Purchase, Vendor.id == Purchase.vendor_id)\
    .filter(Purchase.purchase_date >= start_date, Purchase.status != 'Cancelled')\
    .group_by(Vendor.name).order_by(desc('total_spent')).limit(10).all()
    
    top_vendors = [{"name": r[0], "orders": int(r[1] or 0), "total_spent": float(r[2] or 0)} for r in top_vendors_q]

    return {
        "summary": {
            "total_expense": float(total_expense),
            "total_orders": total_orders,
            "avg_order_value": float(avg_order_value)
        },
        "trend": trend,
        "top_vendors": top_vendors
    }

@router.get("/customers", response_model=dict)
def customers_report(user: User = Depends(require_permission("reports", "view")), db: Session = Depends(get_db)):
    total_customers = db.query(Customer).count()
    active_customers = db.query(Customer).filter(Customer.is_active == True).count()
    
    total_outstanding = db.query(func.sum(Customer.outstanding_amount)).scalar() or 0
    
    # Outstanding Table
    outstanding_q = db.query(Customer).filter(Customer.outstanding_amount > 0).order_by(desc(Customer.outstanding_amount)).limit(50).all()
    outstanding = [{"id": c.id, "name": c.name, "amount": float(c.outstanding_amount or 0), "phone": c.mobile} for c in outstanding_q]
    
    return {
        "summary": {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "total_outstanding": float(total_outstanding)
        },
        "outstanding": outstanding
    }

@router.get("/vendors", response_model=dict)
def vendors_report(user: User = Depends(require_permission("reports", "view")), db: Session = Depends(get_db)):
    total_vendors = db.query(Vendor).count()
    active_vendors = db.query(Vendor).filter(Vendor.is_active == True).count()
    
    total_payable = db.query(func.sum(Vendor.outstanding_amount)).scalar() or 0
    
    # Outstanding Table
    outstanding_q = db.query(Vendor).filter(Vendor.outstanding_amount > 0).order_by(desc(Vendor.outstanding_amount)).limit(50).all()
    outstanding = [{"id": v.id, "name": v.name, "amount": float(v.outstanding_amount or 0), "phone": v.mobile} for v in outstanding_q]
    
    return {
        "summary": {
            "total_vendors": total_vendors,
            "active_vendors": active_vendors,
            "total_payable": float(total_payable)
        },
        "outstanding": outstanding
    }

@router.get("/inventory", response_model=dict)
def inventory_report(user: User = Depends(require_permission("reports", "view")), db: Session = Depends(get_db)):
    total_items = db.query(func.sum(Inventory.quantity)).scalar() or 0
    
    # Valuation: sum(qty * cost_price)
    valuation_q = db.query(
        func.sum(Inventory.quantity * Product.cost_price)
    ).join(Product, Inventory.product_id == Product.id).scalar() or 0
    
    # Low stock items
    low_stock_q = db.query(
        Product.name, Product.sku, Inventory.quantity, Product.min_stock
    ).join(Product, Inventory.product_id == Product.id).filter(Inventory.quantity <= Product.min_stock).limit(50).all()
    
    low_stock = [{"name": r[0], "sku": r[1], "quantity": int(r[2] or 0), "min_stock": int(r[3] or 0)} for r in low_stock_q]
    
    return {
        "summary": {
            "total_items": int(total_items),
            "total_valuation": float(valuation_q),
            "low_stock_count": len(low_stock)
        },
        "low_stock": low_stock
    }

@router.get("/gst", response_model=dict)
def gst_report(days: int = Query(30, ge=1, le=365), user: User = Depends(require_permission("reports", "view")), db: Session = Depends(get_db)):
    start_date, end_date = get_date_range(days)
    
    gst_collected = db.query(func.sum(Sale.tax_amount)).filter(Sale.sale_date >= start_date, Sale.status != 'Cancelled').scalar() or 0
    gst_paid = db.query(func.sum(Purchase.tax_amount)).filter(Purchase.purchase_date >= start_date, Purchase.status != 'Cancelled').scalar() or 0
    
    net_liability = float(gst_collected) - float(gst_paid)
    
    # Simple list of recent taxable sales
    sales_q = db.query(Sale).filter(Sale.sale_date >= start_date, Sale.tax_amount > 0).limit(50).all()
    recent_sales = [{"invoice": s.invoice_number, "date": str(s.sale_date), "amount": float(s.total_amount), "tax": float(s.tax_amount)} for s in sales_q]
    
    return {
        "summary": {
            "gst_collected": float(gst_collected),
            "gst_paid": float(gst_paid),
            "net_liability": net_liability
        },
        "recent_sales": recent_sales
    }
