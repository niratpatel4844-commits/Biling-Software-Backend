from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
import uuid

from app.database import get_db
from app.models.purchase import Purchase, PurchaseItem
from app.models.vendor_payment import VendorPayment
from app.models.inventory import Inventory, StockMovement
from app.models.vendor import Vendor
from app.models.user import User
from app.schemas.schemas import PurchaseCreate, PurchaseResponse, VendorPaymentCreate, VendorPaymentResponse, MessageResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/purchases", tags=["Purchases"])

def generate_po_number(prefix="PO"):
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

@router.post("/", response_model=PurchaseResponse)
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
    
    prefix = "PR" if purchase_data.document_type == "purchase_request" else "PO" if purchase_data.document_type == "purchase_order" else "GRN" if purchase_data.document_type == "goods_receipt" else "PB" if purchase_data.document_type == "purchase_bill" else "VR"
    
    new_purchase = Purchase(
        po_number=generate_po_number(prefix),
        document_type=purchase_data.document_type,
        vendor_id=purchase_data.vendor_id,
        company_id=purchase_data.company_id,
        warehouse_id=purchase_data.warehouse_id,
        branch_id=purchase_data.branch_id,
        priority=purchase_data.priority,
        subtotal=subtotal,
        discount_amount=purchase_data.discount_amount,
        tax_amount=total_tax,
        total_amount=total_amount,
        paid_amount=paid_amount,
        status="completed" if purchase_data.document_type in ["purchase_bill", "vendor_return"] else "pending",
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
            damaged_quantity=item.damaged_quantity,
            return_reason=item.return_reason,
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
            if inventory: inventory.quantity += item.quantity
            else:
                inventory = Inventory(
                    product_id=item.product_id,
                    warehouse_id=purchase_data.warehouse_id,
                    branch_id=purchase_data.branch_id,
                    quantity=item.quantity
                )
                db.add(inventory)
            
            db.add(StockMovement(
                product_id=item.product_id,
                to_type="warehouse" if purchase_data.warehouse_id else "branch",
                to_id=purchase_data.warehouse_id or purchase_data.branch_id,
                quantity=item.quantity,
                movement_type="purchase",
                reference=new_purchase.po_number,
                created_by=current_user.id
            ))
            
        # Decrease Inventory for returns
        if purchase_data.document_type == "vendor_return":
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.warehouse_id == purchase_data.warehouse_id,
                Inventory.branch_id == purchase_data.branch_id
            ).first()
            if inventory: inventory.quantity -= item.quantity
            
            db.add(StockMovement(
                product_id=item.product_id,
                to_type="warehouse" if purchase_data.warehouse_id else "branch",
                to_id=purchase_data.warehouse_id or purchase_data.branch_id,
                quantity=item.quantity,
                movement_type="return",
                reference=new_purchase.po_number,
                created_by=current_user.id
            ))
            
    # Update Vendor Outstanding
    due_amount = float(total_amount) - float(paid_amount)
    if due_amount > 0 and purchase_data.document_type == "purchase_bill":
        vendor = db.query(Vendor).filter(Vendor.id == purchase_data.vendor_id).first()
        if vendor: vendor.outstanding_amount = float(vendor.outstanding_amount or 0) + due_amount
            
    # Decrease Vendor Outstanding for returns
    if purchase_data.document_type == "vendor_return":
        vendor = db.query(Vendor).filter(Vendor.id == purchase_data.vendor_id).first()
        if vendor: vendor.outstanding_amount = max(0, float(vendor.outstanding_amount or 0) - float(total_amount))
            
    db.commit()
    db.refresh(new_purchase)
    return PurchaseResponse.model_validate(new_purchase)

@router.get("/{document_type}", response_model=List[PurchaseResponse])
def get_purchases(document_type: str, db: Session = Depends(get_db)):
    purchases = db.query(Purchase).filter(Purchase.document_type == document_type).order_by(Purchase.id.desc()).all()
    return purchases

@router.get("/details/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase

@router.post("/{purchase_id}/convert/{target_type}", response_model=MessageResponse)
def convert_document(purchase_id: int, target_type: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    source_purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not source_purchase:
        raise HTTPException(status_code=404, detail="Document not found")
        
    prefix = "PR" if target_type == "purchase_request" else "PO" if target_type == "purchase_order" else "GRN" if target_type == "goods_receipt" else "PB" if target_type == "purchase_bill" else "VR"
    
    new_purchase = Purchase(
        po_number=generate_po_number(prefix),
        document_type=target_type,
        reference_id=source_purchase.id,
        vendor_id=source_purchase.vendor_id,
        company_id=source_purchase.company_id,
        warehouse_id=source_purchase.warehouse_id,
        branch_id=source_purchase.branch_id,
        priority=source_purchase.priority,
        subtotal=source_purchase.subtotal,
        discount_amount=source_purchase.discount_amount,
        tax_amount=source_purchase.tax_amount,
        total_amount=source_purchase.total_amount,
        paid_amount=0,
        status="completed" if target_type == "vendor_return" else "pending",
        payment_status="unpaid",
        notes=f"Converted from {source_purchase.document_type} {source_purchase.po_number}",
        created_by=current_user.id
    )
    
    db.add(new_purchase)
    db.flush()
    
    source_purchase.status = "completed"
    
    for item in source_purchase.items:
        new_item = PurchaseItem(
            purchase_id=new_purchase.id,
            product_id=item.product_id,
            product_variant_id=item.product_variant_id,
            unit_id=item.unit_id,
            quantity=item.quantity,
            received_quantity=item.quantity if target_type in ["purchase_bill", "goods_receipt"] else 0,
            unit_price=item.unit_price,
            gst_percent=item.gst_percent,
            total=item.total
        )
        db.add(new_item)
        
        # Increase Inventory for GRN or Bill
        if target_type in ["purchase_bill", "goods_receipt"]:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.warehouse_id == source_purchase.warehouse_id,
                Inventory.branch_id == source_purchase.branch_id
            ).first()
            if inventory: inventory.quantity += item.quantity
            else:
                inventory = Inventory(
                    product_id=item.product_id,
                    warehouse_id=source_purchase.warehouse_id,
                    branch_id=source_purchase.branch_id,
                    quantity=item.quantity
                )
                db.add(inventory)
            
            db.add(StockMovement(
                product_id=item.product_id,
                to_type="warehouse" if source_purchase.warehouse_id else "branch",
                to_id=source_purchase.warehouse_id or source_purchase.branch_id,
                quantity=item.quantity,
                movement_type="purchase",
                reference=new_purchase.po_number,
                created_by=current_user.id
            ))
            
        # Decrease Inventory for returns
        if target_type == "vendor_return":
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.warehouse_id == source_purchase.warehouse_id,
                Inventory.branch_id == source_purchase.branch_id
            ).first()
            if inventory: inventory.quantity -= item.quantity
            
            db.add(StockMovement(
                product_id=item.product_id,
                to_type="warehouse" if source_purchase.warehouse_id else "branch",
                to_id=source_purchase.warehouse_id or source_purchase.branch_id,
                quantity=item.quantity,
                movement_type="return",
                reference=new_purchase.po_number,
                created_by=current_user.id
            ))
            
    # Update Vendor Outstanding if Purchase Bill
    if target_type == "purchase_bill":
        vendor = db.query(Vendor).filter(Vendor.id == source_purchase.vendor_id).first()
        if vendor: vendor.outstanding_amount = float(vendor.outstanding_amount or 0) + float(new_purchase.total_amount)
        
    # Decrease Vendor Outstanding for returns
    if target_type == "vendor_return":
        vendor = db.query(Vendor).filter(Vendor.id == source_purchase.vendor_id).first()
        if vendor: vendor.outstanding_amount = max(0, float(vendor.outstanding_amount or 0) - float(new_purchase.total_amount))
        
    db.commit()
    return {"message": f"Successfully converted to {target_type}", "success": True}

@router.post("/payments", response_model=MessageResponse)
def make_vendor_payment(payment: VendorPaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    vendor = db.query(Vendor).filter(Vendor.id == payment.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    new_payment = VendorPayment(
        payment_number=f"VP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        vendor_id=payment.vendor_id,
        purchase_bill_id=payment.purchase_bill_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        reference_number=payment.reference_number,
        notes=payment.notes,
        created_by=current_user.id
    )
    db.add(new_payment)
    
    vendor.outstanding_amount = max(0, float(vendor.outstanding_amount or 0) - payment.amount)
    
    if payment.purchase_bill_id:
        bill = db.query(Purchase).filter(Purchase.id == payment.purchase_bill_id).first()
        if bill:
            bill.paid_amount = float(bill.paid_amount or 0) + payment.amount
            if float(bill.paid_amount) >= float(bill.total_amount):
                bill.payment_status = "paid"
            else:
                bill.payment_status = "partial"
                
    db.commit()
    return {"message": "Payment recorded successfully", "success": True}

@router.get("/payments/list", response_model=List[VendorPaymentResponse])
def list_vendor_payments(db: Session = Depends(get_db)):
    return db.query(VendorPayment).order_by(VendorPayment.id.desc()).all()
