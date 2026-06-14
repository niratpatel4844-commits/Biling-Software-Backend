from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
import uuid

from app.database import get_db
from app.models.sale import Sale, SaleItem
from app.models.inventory import Inventory, StockMovement
from app.models.customer import Customer
from app.models.user import User
from app.schemas.schemas import SaleCreate, MessageResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/sales", tags=["Sales"])

def generate_invoice_number():
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

@router.post("/", response_model=MessageResponse)
def create_sale(sale_data: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Calculate totals
    subtotal = 0
    total_tax = 0
    
    for item in sale_data.items:
        # Check stock availability
        inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id,
            Inventory.branch_id == sale_data.branch_id,
            Inventory.franchise_id == sale_data.franchise_id
        ).first()
        
        if not inventory or inventory.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product ID {item.product_id}")
            
        item_total = item.quantity * item.unit_price
        item_tax = (item_total * item.gst_percent) / 100
        
        subtotal += item_total
        total_tax += item_tax

    total_amount = subtotal + total_tax
    paid_amount = total_amount if sale_data.payment_status == "paid" else 0
    
    # 2. Create Sale Record
    new_sale = Sale(
        invoice_number=generate_invoice_number(),
        document_type=sale_data.document_type,
        customer_id=sale_data.customer_id,
        company_id=sale_data.company_id,
        branch_id=sale_data.branch_id,
        franchise_id=sale_data.franchise_id,
        warehouse_id=sale_data.warehouse_id,
        sales_person_id=sale_data.sales_person_id,
        subtotal=subtotal,
        tax_amount=total_tax,
        total_amount=total_amount,
        paid_amount=paid_amount,
        due_amount=total_amount - paid_amount,
        payment_method=sale_data.payment_method,
        payment_status=sale_data.payment_status,
        notes=sale_data.notes,
        created_by=current_user.id
    )
    
    db.add(new_sale)
    db.flush() # Get the new_sale.id
    
    # 3. Process Items and Inventory
    for item in sale_data.items:
        item_total = item.quantity * item.unit_price
        item_tax = (item_total * item.gst_percent) / 100
        
        sale_item = SaleItem(
            sale_id=new_sale.id,
            product_id=item.product_id,
            product_variant_id=item.product_variant_id,
            unit_id=item.unit_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount_percent=item.discount_percent,
            gst_percent=item.gst_percent,
            gst_amount=item_tax,
            total=item_total + item_tax
        )
        db.add(sale_item)
        
        # Adjust Inventory if it's an invoice or sales_order
        # Actually standard ERP deducts on invoice or delivery, reserves on order.
        # For simplicity we deduct on invoice.
        if sale_data.document_type in ["invoice"]:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.branch_id == sale_data.branch_id,
                Inventory.franchise_id == sale_data.franchise_id
            ).first()
            
            inventory.quantity -= item.quantity
            
            movement = StockMovement(
                product_id=item.product_id,
                from_type="branch" if sale_data.branch_id else "franchise",
                from_id=sale_data.branch_id or sale_data.franchise_id,
                quantity=-item.quantity,
                movement_type="sale",
                reference=new_sale.invoice_number,
                created_by=current_user.id
            )
            db.add(movement)
            
    # Update Customer Outstanding
    if new_sale.due_amount > 0:
        customer = db.query(Customer).filter(Customer.id == sale_data.customer_id).first()
        if customer:
            customer.outstanding_amount += new_sale.due_amount
            
    db.commit()
    return {"message": "Sale created successfully", "success": True}
