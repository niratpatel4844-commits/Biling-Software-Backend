from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
import uuid

from app.database import get_db
from app.models.purchase import Purchase, PurchaseItem
from app.models.inventory import Inventory, StockMovement
from app.models.vendor import Vendor
from app.models.user import User
from app.schemas.schemas import PurchaseCreate, MessageResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/purchases", tags=["Purchases"])

def generate_po_number():
    return f"PO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

@router.post("/", response_model=MessageResponse)
def create_purchase(purchase_data: PurchaseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subtotal = 0
    total_tax = 0
    
    for item in purchase_data.items:
        item_total = item.quantity * item.unit_price
        item_tax = (item_total * item.gst_percent) / 100
        
        subtotal += item_total
        total_tax += item_tax

    total_amount = subtotal + total_tax
    paid_amount = total_amount if purchase_data.payment_status == "paid" else 0
    
    new_purchase = Purchase(
        po_number=generate_po_number(),
        document_type=purchase_data.document_type,
        vendor_id=purchase_data.vendor_id,
        company_id=purchase_data.company_id,
        warehouse_id=purchase_data.warehouse_id,
        branch_id=purchase_data.branch_id,
        subtotal=subtotal,
        discount_amount=purchase_data.discount_amount,
        tax_amount=total_tax,
        total_amount=total_amount,
        paid_amount=paid_amount,
        status="completed" if purchase_data.document_type == "purchase_bill" else "pending",
        payment_status=purchase_data.payment_status,
        notes=purchase_data.notes,
        created_by=current_user.id
    )
    
    db.add(new_purchase)
    db.flush()
    
    for item in purchase_data.items:
        item_total = item.quantity * item.unit_price
        
        purchase_item = PurchaseItem(
            purchase_id=new_purchase.id,
            product_id=item.product_id,
            product_variant_id=item.product_variant_id,
            unit_id=item.unit_id,
            quantity=item.quantity,
            received_quantity=item.quantity if purchase_data.document_type in ["purchase_bill", "goods_receipt"] else 0,
            unit_price=item.unit_price,
            gst_percent=item.gst_percent,
            total=item_total
        )
        db.add(purchase_item)
        
        # Increase Inventory
        if purchase_data.document_type in ["purchase_bill", "goods_receipt"]:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.warehouse_id == purchase_data.warehouse_id,
                Inventory.branch_id == purchase_data.branch_id
            ).first()
            
            if inventory:
                inventory.quantity += item.quantity
            else:
                inventory = Inventory(
                    product_id=item.product_id,
                    warehouse_id=purchase_data.warehouse_id,
                    branch_id=purchase_data.branch_id,
                    quantity=item.quantity
                )
                db.add(inventory)
            
            movement = StockMovement(
                product_id=item.product_id,
                to_type="warehouse" if purchase_data.warehouse_id else "branch",
                to_id=purchase_data.warehouse_id or purchase_data.branch_id,
                quantity=item.quantity,
                movement_type="purchase",
                reference=new_purchase.po_number,
                created_by=current_user.id
            )
            db.add(movement)
            
    # Update Vendor Outstanding
    due_amount = total_amount - paid_amount
    if due_amount > 0:
        vendor = db.query(Vendor).filter(Vendor.id == purchase_data.vendor_id).first()
        if vendor:
            vendor.outstanding_amount += due_amount
            
    db.commit()
    return {"message": "Purchase created successfully", "success": True}
