from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import uuid

from app.database import get_db
from app.models.sale import Sale, SaleItem
from app.models.inventory import Inventory, StockMovement
from app.models.customer import Customer
from app.models.user import User
from app.models.delivery_challan import DeliveryChallan, DeliveryChallanItem
from app.models.customer_payment import CustomerPayment
from app.schemas.schemas import (
    SaleCreate, MessageResponse, SaleResponse, 
    CustomerPaymentCreate, CustomerPaymentResponse,
    DeliveryChallanCreate, DeliveryChallanResponse
)
from app.routers.auth import get_current_user
router = APIRouter(prefix="/api/sales", tags=["Sales"])

def generate_document_number(doc_type: str):
    prefix = {
        "quotation": "QT",
        "sales_order": "SO",
        "invoice": "INV",
        "return": "RET",
        "credit_note": "CN"
    }.get(doc_type, "DOC")
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

@router.post("/", response_model=MessageResponse)
def create_sale_document(sale_data: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Calculate totals
    subtotal = 0
    total_tax = 0
    
    for item in sale_data.items:
        # Check stock for invoices only
        if sale_data.document_type == "invoice":
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.branch_id == sale_data.branch_id,
                Inventory.franchise_id == sale_data.franchise_id
            ).first()
            if not inventory or inventory.quantity < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product ID {item.product_id}")
                
        item_total = item.quantity * item.unit_price
        item_discount = (item_total * (item.discount_percent or 0)) / 100
        item_total_after_discount = item_total - item_discount
        item_tax = (item_total_after_discount * (item.gst_percent or 0)) / 100
        
        subtotal += item_total_after_discount
        total_tax += item_tax

    total_amount = subtotal + total_tax
    paid_amount = total_amount if sale_data.payment_status == "paid" else 0
    if sale_data.document_type in ["quotation", "sales_order", "return", "credit_note"]:
        paid_amount = 0 # No payment at this stage usually, or handled separately
        
    doc_status = "draft" if sale_data.document_type == "quotation" else "pending"
    if sale_data.document_type == "invoice":
        doc_status = "completed"

    new_sale = Sale(
        invoice_number=generate_document_number(sale_data.document_type),
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
        status=doc_status,
        notes=sale_data.notes,
        created_by=current_user.id
    )
    
    db.add(new_sale)
    db.flush()
    
    for item in sale_data.items:
        item_price = float(item.unit_price)
        item_qty = int(item.quantity)
        item_total = item_price * item_qty
        
        # Clamp discount percent to max 100
        safe_discount_percent = min(float(item.discount_percent or 0), 100.0)
        item_discount = (item_total * safe_discount_percent) / 100
        item_taxable = item_total - item_discount
        item_tax = (item_taxable * float(item.gst_percent or 0)) / 100
        
        sale_item = SaleItem(
            sale_id=new_sale.id,
            product_id=item.product_id,
            product_variant_id=item.product_variant_id,
            unit_id=item.unit_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount_percent=safe_discount_percent,
            discount_amount=item_discount,
            gst_percent=item.gst_percent,
            gst_amount=item_tax,
            total=item_taxable + item_tax
        )
        db.add(sale_item)
        
        # Deduct Inventory if it's an invoice
        if sale_data.document_type == "invoice":
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
            
    # Update Customer Outstanding only for Invoice
    if sale_data.document_type == "invoice" and new_sale.due_amount > 0:
        customer = db.query(Customer).filter(Customer.id == sale_data.customer_id).first()
        if customer:
            customer.outstanding_amount = (customer.outstanding_amount or 0) + new_sale.due_amount
            
    db.commit()
    return {"message": f"{sale_data.document_type.capitalize()} created successfully", "success": True}


@router.post("/returns/{return_id}/approve", response_model=MessageResponse)
def approve_return(return_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sale_return = db.query(Sale).filter(Sale.id == return_id, Sale.document_type == "return").first()
    if not sale_return:
        raise HTTPException(status_code=404, detail="Return document not found")
        
    sale_return.status = "approved"
    
    for item in sale_return.items:
        inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id,
            Inventory.branch_id == sale_return.branch_id,
            Inventory.franchise_id == sale_return.franchise_id
        ).first()
        if inventory:
            inventory.quantity += item.quantity
            movement = StockMovement(
                product_id=item.product_id,
                from_type="branch" if sale_return.branch_id else "franchise",
                from_id=sale_return.branch_id or sale_return.franchise_id,
                quantity=item.quantity,
                movement_type="sales_return",
                reference=sale_return.invoice_number,
                created_by=current_user.id
            )
            db.add(movement)
            
    # Also create a credit note or adjust customer balance
    customer = db.query(Customer).filter(Customer.id == sale_return.customer_id).first()
    if customer:
        customer.outstanding_amount = max(0, float(customer.outstanding_amount or 0) - float(sale_return.total_amount))
        
    db.commit()
    return {"message": "Return approved and inventory restocked", "success": True}

@router.post("/payments", response_model=MessageResponse)
def receive_payment(payment: CustomerPaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_payment = CustomerPayment(
        receipt_number=f"REC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        customer_id=payment.customer_id,
        invoice_id=payment.invoice_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        reference_number=payment.reference_number,
        notes=payment.notes,
        created_by=current_user.id
    )
    db.add(new_payment)
    
    customer = db.query(Customer).filter(Customer.id == payment.customer_id).first()
    if customer:
        customer.outstanding_amount = max(0, float(customer.outstanding_amount or 0) - payment.amount)
        
    if payment.invoice_id:
        invoice = db.query(Sale).filter(Sale.id == payment.invoice_id).first()
        if invoice:
            invoice.paid_amount = float(invoice.paid_amount or 0) + payment.amount
            invoice.due_amount = float(invoice.total_amount or 0) - invoice.paid_amount
            if invoice.due_amount <= 0:
                invoice.payment_status = "paid"
            else:
                invoice.payment_status = "partial"
                
    db.commit()
    return {"message": "Payment recorded successfully", "success": True}

@router.get("/payments/list", response_model=List[CustomerPaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    return db.query(CustomerPayment).order_by(CustomerPayment.id.desc()).all()

@router.post("/challans", response_model=MessageResponse)
def create_delivery_challan(challan: DeliveryChallanCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_challan = DeliveryChallan(
        challan_number=f"DC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        customer_id=challan.customer_id,
        sales_order_id=challan.sales_order_id,
        delivery_address=challan.delivery_address,
        vehicle_details=challan.vehicle_details,
        driver_name=challan.driver_name,
        status=challan.status,
        created_by=current_user.id
    )
    db.add(new_challan)
    db.flush()
    
    for item in challan.items:
        dc_item = DeliveryChallanItem(
            challan_id=new_challan.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(dc_item)
        
    db.commit()
    return {"message": "Delivery Challan created successfully", "success": True}

@router.get("/challans/list", response_model=List[DeliveryChallanResponse])
def get_challans(db: Session = Depends(get_db)):
    return db.query(DeliveryChallan).order_by(DeliveryChallan.id.desc()).all()

@router.get("/details/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Document not found")
    return sale

@router.get("/{document_type}", response_model=List[SaleResponse])
def get_sales_documents(document_type: str, db: Session = Depends(get_db)):
    return db.query(Sale).filter(Sale.document_type == document_type).order_by(Sale.id.desc()).all()

@router.post("/{sale_id}/convert/{target_type}", response_model=MessageResponse)
def convert_document(sale_id: int, target_type: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    source_sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not source_sale:
        raise HTTPException(status_code=404, detail="Document not found")
        
    new_doc = Sale(
        invoice_number=generate_document_number(target_type),
        document_type=target_type,
        reference_id=source_sale.id,
        customer_id=source_sale.customer_id,
        company_id=source_sale.company_id,
        branch_id=source_sale.branch_id,
        franchise_id=source_sale.franchise_id,
        warehouse_id=source_sale.warehouse_id,
        sales_person_id=source_sale.sales_person_id,
        subtotal=source_sale.subtotal,
        tax_amount=source_sale.tax_amount,
        total_amount=source_sale.total_amount,
        due_amount=source_sale.total_amount,
        payment_status="unpaid",
        status="pending" if target_type != "invoice" else "completed",
        created_by=current_user.id
    )
    db.add(new_doc)
    db.flush()
    
    for item in source_sale.items:
        new_item = SaleItem(
            sale_id=new_doc.id,
            product_id=item.product_id,
            product_variant_id=item.product_variant_id,
            unit_id=item.unit_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount_percent=item.discount_percent,
            discount_amount=item.discount_amount,
            gst_percent=item.gst_percent,
            gst_amount=item.gst_amount,
            total=item.total
        )
        db.add(new_item)
        
        if target_type == "invoice":
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.branch_id == source_sale.branch_id,
                Inventory.franchise_id == source_sale.franchise_id
            ).first()
            if inventory:
                inventory.quantity -= item.quantity
                movement = StockMovement(
                    product_id=item.product_id,
                    from_type="branch" if source_sale.branch_id else "franchise",
                    from_id=source_sale.branch_id or source_sale.franchise_id,
                    quantity=-item.quantity,
                    movement_type="sale",
                    reference=new_doc.invoice_number,
                    created_by=current_user.id
                )
                db.add(movement)
    
    if target_type == "invoice":
        customer = db.query(Customer).filter(Customer.id == source_sale.customer_id).first()
        if customer:
            customer.outstanding_amount = (customer.outstanding_amount or 0) + new_doc.due_amount
            
    source_sale.status = "converted"
    db.commit()
    return {"message": f"Successfully converted to {target_type}", "success": True}
