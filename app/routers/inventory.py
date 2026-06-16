from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.inventory import Inventory, StockMovement, StockHistory
from app.models.product import Product
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.schemas import InventoryResponse, OpeningStockRequest, StockMovementRequest, StockMovementResponse, StockHistoryResponse
from app.utils.auth import require_permission
import math
from datetime import datetime

router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])

@router.get("/", response_model=dict)
def list_inventory(
    page: int = Query(1, ge=1), 
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    user: User = Depends(require_permission("inventory", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Inventory, Product).join(Product, Inventory.product_id == Product.id)
    
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
        
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for inv, prod in items:
        inv_data = InventoryResponse.model_validate(inv).model_dump()
        inv_data["product_name"] = prod.name
        inv_data["product_sku"] = prod.sku
        result.append(inv_data)
        
    return {
        "items": result,
        "total": total, 
        "page": page, 
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 1
    }

@router.post("/opening-stock", response_model=InventoryResponse)
def add_opening_stock(data: OpeningStockRequest, user: User = Depends(require_permission("inventory", "create")), db: Session = Depends(get_db)):
    if data.opening_quantity < 0:
        raise HTTPException(status_code=400, detail="Opening quantity cannot be negative")
    if data.reserved_quantity > data.opening_quantity:
        raise HTTPException(status_code=400, detail="Reserved quantity cannot exceed opening quantity")
    if data.damaged_quantity > data.opening_quantity:
        raise HTTPException(status_code=400, detail="Damaged quantity cannot exceed opening quantity")

    # Check if inventory record already exists for this product in this location
    inv_query = db.query(Inventory).filter(
        Inventory.product_id == data.product_id,
        Inventory.warehouse_id == data.warehouse_id
    )
    if inv_query.first():
        raise HTTPException(status_code=400, detail="Opening stock already added for this product in this warehouse. Use Adjustments or Purchases for future stock changes.")

    # Create new inventory record
    inv = Inventory(
        product_id=data.product_id,
        branch_id=data.branch_id,
        warehouse_id=data.warehouse_id,
        franchise_id=data.franchise_id,
        quantity=data.opening_quantity,
        reserved_quantity=data.reserved_quantity,
        damaged_quantity=data.damaged_quantity,
        batch_number=data.batch_number,
        expiry_date=data.expiry_date,
        last_restocked=data.opening_stock_date or datetime.utcnow()
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # Create stock history record
    stock_history = StockHistory(
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        branch_id=data.branch_id,
        company_id=data.company_id,
        transaction_type="OPENING_STOCK",
        previous_stock=0,
        quantity_in=data.opening_quantity,
        quantity_out=0,
        new_stock=data.opening_quantity,
        reference_id=str(inv.id),
        remarks=data.remarks or "Opening Stock Entry",
        created_by=user.id
    )
    db.add(stock_history)
    
    # Optionally update cost and price of the product if provided
    if data.purchase_cost is not None or data.selling_price is not None:
        product = db.query(Product).filter(Product.id == data.product_id).first()
        if product:
            if data.purchase_cost is not None:
                product.cost_price = data.purchase_cost
            if data.selling_price is not None:
                product.selling_price = data.selling_price
                
    db.commit()
    db.refresh(inv)
    
    return InventoryResponse.model_validate(inv)

@router.get("/movements", response_model=dict)
def list_movements(
    page: int = Query(1, ge=1), 
    page_size: int = Query(20, ge=1, le=100),
    movement_type: Optional[str] = Query(None),
    user: User = Depends(require_permission("inventory", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(StockMovement).order_by(StockMovement.created_at.desc())
    if movement_type:
        q = q.filter(StockMovement.movement_type == movement_type)
        
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for mov in items:
        prod = db.query(Product).filter(Product.id == mov.product_id).first()
        mov_data = StockMovementResponse.model_validate(mov).model_dump()
        mov_data["product_name"] = prod.name if prod else "Unknown"
        mov_data["product_sku"] = prod.sku if prod else "Unknown"
        result.append(mov_data)
        
    return {
        "items": result,
        "total": total, 
        "page": page, 
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 1
    }

@router.post("/movements", response_model=StockMovementResponse)
def create_movement(data: StockMovementRequest, user: User = Depends(require_permission("inventory", "create")), db: Session = Depends(get_db)):
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    # Helper function to get or create inventory
    def get_inventory(warehouse_id):
        inv = db.query(Inventory).filter(
            Inventory.product_id == data.product_id,
            Inventory.warehouse_id == warehouse_id
        ).first()
        if not inv:
            inv = Inventory(product_id=data.product_id, warehouse_id=warehouse_id, quantity=0)
            db.add(inv)
            db.flush()
        return inv

    mov = StockMovement(
        product_id=data.product_id,
        quantity=data.quantity,
        movement_type=data.movement_type,
        reference=data.reference,
        notes=data.notes,
        created_by=user.id
    )

    if data.movement_type == 'transfer':
        if not data.from_warehouse_id or not data.to_warehouse_id:
            raise HTTPException(status_code=400, detail="Transfer requires both source and destination warehouses")
        
        src_inv = get_inventory(data.from_warehouse_id)
        if src_inv.quantity < data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock in source warehouse")
            
        dst_inv = get_inventory(data.to_warehouse_id)
        
        src_inv.quantity -= data.quantity
        dst_inv.quantity += data.quantity
        
        mov.from_type = 'warehouse'
        mov.from_id = data.from_warehouse_id
        mov.to_type = 'warehouse'
        mov.to_id = data.to_warehouse_id

        # Log Source History
        db.add(StockHistory(
            product_id=data.product_id, warehouse_id=data.from_warehouse_id, transaction_type="TRANSFER_OUT",
            previous_stock=src_inv.quantity + data.quantity, quantity_in=0, quantity_out=data.quantity,
            new_stock=src_inv.quantity, remarks=data.notes, created_by=user.id
        ))
        # Log Dest History
        db.add(StockHistory(
            product_id=data.product_id, warehouse_id=data.to_warehouse_id, transaction_type="TRANSFER_IN",
            previous_stock=dst_inv.quantity - data.quantity, quantity_in=data.quantity, quantity_out=0,
            new_stock=dst_inv.quantity, remarks=data.notes, created_by=user.id
        ))

    elif data.movement_type == 'adjustment_in':
        if not data.to_warehouse_id:
            raise HTTPException(status_code=400, detail="Destination warehouse required")
            
        inv = get_inventory(data.to_warehouse_id)
        prev_stock = inv.quantity
        inv.quantity += data.quantity
        
        mov.to_type = 'warehouse'
        mov.to_id = data.to_warehouse_id

        db.add(StockHistory(
            product_id=data.product_id, warehouse_id=data.to_warehouse_id, transaction_type="ADJUSTMENT_IN",
            previous_stock=prev_stock, quantity_in=data.quantity, quantity_out=0,
            new_stock=inv.quantity, remarks=data.notes, created_by=user.id
        ))

    elif data.movement_type == 'adjustment_out':
        if not data.from_warehouse_id:
            raise HTTPException(status_code=400, detail="Source warehouse required")
            
        inv = get_inventory(data.from_warehouse_id)
        if inv.quantity < data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock to remove")
            
        prev_stock = inv.quantity
        inv.quantity -= data.quantity
        
        mov.from_type = 'warehouse'
        mov.from_id = data.from_warehouse_id

        db.add(StockHistory(
            product_id=data.product_id, warehouse_id=data.from_warehouse_id, transaction_type="ADJUSTMENT_OUT",
            previous_stock=prev_stock, quantity_in=0, quantity_out=data.quantity,
            new_stock=inv.quantity, remarks=data.notes, created_by=user.id
        ))

    elif data.movement_type == 'damage':
        if not data.from_warehouse_id:
            raise HTTPException(status_code=400, detail="Source warehouse required")
            
        inv = get_inventory(data.from_warehouse_id)
        if inv.quantity < data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock to mark as damaged")
            
        prev_stock = inv.quantity
        inv.quantity -= data.quantity
        inv.damaged_quantity = (inv.damaged_quantity or 0) + data.quantity
        
        mov.from_type = 'warehouse'
        mov.from_id = data.from_warehouse_id

        db.add(StockHistory(
            product_id=data.product_id, warehouse_id=data.from_warehouse_id, transaction_type="DAMAGE",
            previous_stock=prev_stock, quantity_in=0, quantity_out=data.quantity,
            new_stock=inv.quantity, remarks=data.notes, created_by=user.id
        ))

    db.add(mov)
    db.commit()
    db.refresh(mov)
    
    return StockMovementResponse.model_validate(mov)

@router.get("/reserved", response_model=dict)
def list_reserved_stock(
    page: int = Query(1, ge=1), 
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    user: User = Depends(require_permission("inventory", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(Inventory, Product).join(Product, Inventory.product_id == Product.id).filter(Inventory.reserved_quantity > 0)
    
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
        
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for inv, prod in items:
        inv_data = InventoryResponse.model_validate(inv).model_dump()
        inv_data["product_name"] = prod.name
        inv_data["product_sku"] = prod.sku
        result.append(inv_data)
        
    return {
        "items": result,
        "total": total, 
        "page": page, 
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 1
    }

@router.get("/history", response_model=dict)
def list_stock_history(
    page: int = Query(1, ge=1), 
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    user: User = Depends(require_permission("inventory", "view")),
    db: Session = Depends(get_db)
):
    q = db.query(StockHistory, Product, Warehouse, User).join(Product, StockHistory.product_id == Product.id).outerjoin(Warehouse, StockHistory.warehouse_id == Warehouse.id).outerjoin(User, StockHistory.created_by == User.id).order_by(StockHistory.created_at.desc())
    
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
        
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for hist, prod, wh, usr in items:
        hist_data = StockHistoryResponse.model_validate(hist).model_dump()
        hist_data["product_name"] = prod.name if prod else "Unknown"
        hist_data["product_sku"] = prod.sku if prod else "Unknown"
        hist_data["warehouse_name"] = wh.name if wh else "-"
        hist_data["user_name"] = usr.full_name if usr else "System"
        result.append(hist_data)
        
    return {
        "items": result,
        "total": total, 
        "page": page, 
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 1
    }
