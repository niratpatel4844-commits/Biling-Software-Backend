from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# --- Auth ---
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class RefreshTokenRequest(BaseModel):
    refresh_token: str


# --- User ---
class UserCreate(BaseModel):
    full_name: str
    email: str
    mobile: Optional[str] = None
    password: str
    role_id: Optional[int] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    company_id: Optional[int] = None
    branch_id: Optional[int] = None
    franchise_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    is_active: Optional[bool] = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    role_id: Optional[int] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    company_id: Optional[int] = None
    branch_id: Optional[int] = None
    franchise_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserResetPassword(BaseModel):
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    mobile: Optional[str] = None
    role_id: Optional[int] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    company_id: Optional[int] = None
    branch_id: Optional[int] = None
    franchise_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    is_active: bool
    is_superadmin: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Role ---
class RoleCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    allow_company: Optional[bool] = True
    allow_branch: Optional[bool] = False
    allow_franchise: Optional[bool] = False
    allow_warehouse: Optional[bool] = False

class RoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    allow_company: Optional[bool] = None
    allow_branch: Optional[bool] = None
    allow_franchise: Optional[bool] = None
    allow_warehouse: Optional[bool] = None

class RoleResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    is_system: bool
    is_active: bool
    allow_company: bool
    allow_branch: bool
    allow_franchise: bool
    allow_warehouse: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Permission ---
class PermissionCreate(BaseModel):
    module: str
    action: str
    name: str
    display_name: str
    description: Optional[str] = None

class PermissionResponse(BaseModel):
    id: int
    module: str
    action: str
    name: str
    display_name: str

    class Config:
        from_attributes = True

class RolePermissionAssign(BaseModel):
    permission_ids: list[int]


# --- Company ---
class CompanyCreate(BaseModel):
    name: str
    company_code: str
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    pincode: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    logo: Optional[str] = None
    currency: Optional[str] = "INR"
    timezone: Optional[str] = "Asia/Kolkata"
    is_active: Optional[bool] = True

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    company_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    logo: Optional[str] = None
    is_active: Optional[bool] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    company_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    logo: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Branch ---
class BranchCreate(BaseModel):
    company_id: int
    name: str
    code: str
    gst_number: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    pincode: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = True

class BranchUpdate(BaseModel):
    company_id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    gst_number: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None

class BranchResponse(BaseModel):
    id: int
    company_id: int
    name: str
    code: str
    gst_number: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Franchise ---
class FranchiseCreate(BaseModel):
    name: str
    code: str
    company_id: int
    owner_name: str
    owner_email: Optional[str] = None
    owner_mobile: Optional[str] = None
    commission_percent: Optional[float] = 0
    royalty_percent: Optional[float] = 0
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    status: Optional[str] = "pending"
    is_active: Optional[bool] = True

class FranchiseUpdate(BaseModel):
    company_id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_mobile: Optional[str] = None
    commission_percent: Optional[float] = None
    royalty_percent: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class FranchiseResponse(BaseModel):
    id: int
    name: str
    code: str
    company_id: int
    owner_name: str
    owner_email: Optional[str] = None
    owner_mobile: Optional[str] = None
    commission_percent: Optional[float] = None
    royalty_percent: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    status: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Warehouse ---
class WarehouseCreate(BaseModel):
    name: str
    code: str
    company_id: int
    branch_id: Optional[int] = None
    manager_id: Optional[int] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    capacity: Optional[str] = None

class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    branch_id: Optional[int] = None
    manager_id: Optional[int] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    capacity: Optional[str] = None
    is_active: Optional[bool] = None

class WarehouseResponse(BaseModel):
    id: int
    name: str
    code: str
    company_id: int
    branch_id: Optional[int] = None
    manager_id: Optional[int] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    capacity: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Product ---
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    child_category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_id: Optional[int] = None
    gst_percent: Optional[float] = 18
    hsn_code: Optional[str] = None
    cost_price: float
    selling_price: float
    mrp: Optional[float] = None
    min_stock: Optional[int] = 10
    reorder_level: Optional[int] = 20
    barcode: Optional[str] = None
    image: Optional[str] = None
    is_active: Optional[bool] = True
    company_id: Optional[int] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    child_category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_id: Optional[int] = None
    gst_percent: Optional[float] = None
    hsn_code: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    mrp: Optional[float] = None
    min_stock: Optional[int] = None
    reorder_level: Optional[int] = None
    barcode: Optional[str] = None
    image: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_id: Optional[int] = None
    gst_percent: Optional[float] = None
    hsn_code: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    mrp: Optional[float] = None
    min_stock: Optional[int] = None
    reorder_level: Optional[int] = None
    barcode: Optional[str] = None
    image: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Brand ---
class BrandCreate(BaseModel):
    name: str
    brand_code: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    is_active: Optional[bool] = True

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    brand_code: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    is_active: Optional[bool] = None

class BrandResponse(BaseModel):
    id: int
    name: str
    brand_code: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Unit ---
class UnitCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

class UnitUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class UnitResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Product Variant ---
class ProductVariantCreate(BaseModel):
    product_id: int
    name: str
    sku: str
    color: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    barcode: Optional[str] = None
    is_active: Optional[bool] = True

class ProductVariantUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    barcode: Optional[str] = None
    is_active: Optional[bool] = None

class ProductVariantResponse(BaseModel):
    id: int
    product_id: int
    name: str
    sku: str
    color: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    barcode: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Category ---
class CategoryCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    category_code: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    main_category_id: Optional[int] = None
    level: Optional[int] = 0
    is_active: Optional[bool] = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    category_code: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    main_category_id: Optional[int] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    category_code: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    level: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Customer ---
class CustomerCreate(BaseModel):
    customer_code: Optional[str] = None
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    credit_limit: Optional[float] = 0
    company_id: Optional[int] = None
    notes: Optional[str] = None

class CustomerResponse(BaseModel):
    id: int
    customer_code: Optional[str] = None
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    credit_limit: Optional[float] = None
    outstanding_amount: Optional[float] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Vendor ---
class VendorCreate(BaseModel):
    vendor_code: Optional[str] = None
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    payment_terms: Optional[str] = None
    company_id: Optional[int] = None
    notes: Optional[str] = None

class VendorResponse(BaseModel):
    id: int
    vendor_code: Optional[str] = None
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    payment_terms: Optional[str] = None
    outstanding_amount: Optional[float] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Audit Log ---
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    module: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    device: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Notification ---
class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Inventory ---
class InventoryResponse(BaseModel):
    id: int
    product_id: int
    branch_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    quantity: int
    reserved_quantity: int
    damaged_quantity: int
    batch_number: Optional[str] = None
    location: Optional[str] = None
    last_restocked: Optional[datetime] = None
    
    # Nested fields for frontend display
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    
    class Config:
        from_attributes = True


# --- Generic ---
class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
    id: int
    product_id: int
    name: str
    sku: str
    color: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    barcode: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Category ---
class CategoryCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    category_code: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    main_category_id: Optional[int] = None
    level: Optional[int] = 0
    is_active: Optional[bool] = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    category_code: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    main_category_id: Optional[int] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    category_code: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    level: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Customer ---
class CustomerCreate(BaseModel):
    customer_code: Optional[str] = None
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    credit_limit: Optional[float] = 0
    company_id: Optional[int] = None
    notes: Optional[str] = None

class CustomerResponse(BaseModel):
    id: int
    customer_code: Optional[str] = None
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    credit_limit: Optional[float] = None
    outstanding_amount: Optional[float] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Vendor ---
class VendorCreate(BaseModel):
    vendor_code: Optional[str] = None
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    payment_terms: Optional[str] = None
    company_id: Optional[int] = None
    notes: Optional[str] = None

class VendorResponse(BaseModel):
    id: int
    vendor_code: Optional[str] = None
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    payment_terms: Optional[str] = None
    outstanding_amount: Optional[float] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Audit Log ---
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    module: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    device: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Notification ---
class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Inventory ---

class OpeningStockRequest(BaseModel):
    product_id: int
    product_variant_id: Optional[int] = None
    opening_quantity: int
    reserved_quantity: int = 0
    damaged_quantity: int = 0
    
    company_id: int
    branch_id: int
    franchise_id: Optional[int] = None
    warehouse_id: int
    
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturing_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    
    purchase_cost: Optional[float] = None
    selling_price: Optional[float] = None
    
    opening_stock_date: Optional[datetime] = None
    remarks: Optional[str] = None

class InventoryCreate(BaseModel):
    product_id: int
    branch_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    quantity: int = 0
    reserved_quantity: int = 0
    damaged_quantity: int = 0
    batch_number: Optional[str] = None
    location: Optional[str] = None

class InventoryResponse(BaseModel):
    id: int
    product_id: int
    branch_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    quantity: int
    reserved_quantity: int
    damaged_quantity: int
    batch_number: Optional[str] = None
    location: Optional[str] = None
    last_restocked: Optional[datetime] = None
    
    # Nested fields for frontend display
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    
    class Config:
        from_attributes = True


# --- Generic ---
class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int

class MessageResponse(BaseModel):
    message: str
    success: bool = True

# --- Sales & Purchases ---
class SaleItemCreate(BaseModel):
    product_id: int
    product_variant_id: Optional[int] = None
    unit_id: Optional[int] = None
    quantity: int
    unit_price: float
    discount_percent: Optional[float] = 0
    gst_percent: Optional[float] = 0

class SaleCreate(BaseModel):
    customer_id: int
    company_id: Optional[int] = None
    document_type: str = "invoice"
    branch_id: Optional[int] = None
    franchise_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    sales_person_id: Optional[int] = None
    payment_method: Optional[str] = None
    payment_status: str = "unpaid"
    notes: Optional[str] = None
    items: list[SaleItemCreate]

class PurchaseItemCreate(BaseModel):
    product_id: int
    product_variant_id: Optional[int] = None
    unit_id: Optional[int] = None
    quantity: int
    unit_price: float
    gst_percent: Optional[float] = 0
    damaged_quantity: Optional[int] = 0
    return_reason: Optional[str] = None

class PurchaseCreate(BaseModel):
    vendor_id: int
    company_id: Optional[int] = None
    document_type: str = "purchase_bill"
    priority: str = "Medium"
    warehouse_id: Optional[int] = None
    branch_id: Optional[int] = None
    discount_amount: Optional[float] = 0
    payment_status: str = "unpaid"
    notes: Optional[str] = None
    items: list[PurchaseItemCreate]

class PurchaseItemResponse(BaseModel):
    id: int
    product_id: int
    product_variant_id: Optional[int] = None
    unit_id: Optional[int] = None
    quantity: int
    unit_price: float
    gst_percent: float
    total: float
    damaged_quantity: Optional[int] = 0
    return_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

class PurchaseResponse(BaseModel):
    id: int
    po_number: str
    document_type: str
    vendor_id: int
    subtotal: float
    tax_amount: float
    total_amount: float
    paid_amount: float
    priority: str
    status: str
    payment_status: str
    purchase_date: Optional[datetime] = None
    items: list[PurchaseItemResponse] = []

    class Config:
        from_attributes = True

class VendorPaymentCreate(BaseModel):
    vendor_id: int
    purchase_bill_id: Optional[int] = None
    amount: float
    payment_method: str = 'Cash'
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class VendorPaymentResponse(BaseModel):
    id: int
    payment_number: str
    payment_date: Optional[datetime] = None
    vendor_id: int
    purchase_bill_id: Optional[int] = None
    amount: float
    payment_method: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# --- Delivery Challan ---
class DeliveryChallanItemCreate(BaseModel):
    product_id: int
    quantity: int

class DeliveryChallanCreate(BaseModel):
    customer_id: int
    sales_order_id: Optional[int] = None
    delivery_address: Optional[str] = None
    vehicle_details: Optional[str] = None
    driver_name: Optional[str] = None
    status: str = 'Pending'
    items: list[DeliveryChallanItemCreate]

class DeliveryChallanResponse(BaseModel):
    id: int
    challan_number: str
    date: Optional[datetime] = None
    customer_id: int
    sales_order_id: Optional[int] = None
    delivery_address: Optional[str] = None
    vehicle_details: Optional[str] = None
    driver_name: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

# --- Customer Payment ---
class CustomerPaymentCreate(BaseModel):
    customer_id: int
    invoice_id: Optional[int] = None
    amount: float
    payment_method: str = 'Cash'
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class CustomerPaymentResponse(BaseModel):
    id: int
    receipt_number: str
    payment_date: Optional[datetime] = None
    customer_id: int
    invoice_id: Optional[int] = None
    amount: float
    payment_method: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    product_variant_id: Optional[int] = None
    unit_id: Optional[int] = None
    quantity: int
    unit_price: float
    discount_percent: float
    discount_amount: float
    gst_percent: float
    gst_amount: float
    total: float
    
    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    document_type: str
    customer_id: int
    subtotal: float
    tax_amount: float
    total_amount: float
    paid_amount: float
    due_amount: float
    payment_status: str
    status: str
    sale_date: Optional[datetime] = None
    items: list[SaleItemResponse] = []

    class Config:
        from_attributes = True



class CustomerUpdate(BaseModel):
    customer_code: Optional[str] = None
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    credit_limit: Optional[float] = None
    company_id: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class VendorUpdate(BaseModel):
    vendor_code: Optional[str] = None
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    payment_terms: Optional[str] = None
    company_id: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class StockMovementRequest(BaseModel):
    product_id: int
    movement_type: str # 'transfer', 'adjustment_in', 'adjustment_out', 'damage'
    from_warehouse_id: Optional[int] = None
    to_warehouse_id: Optional[int] = None
    quantity: int
    notes: Optional[str] = None
    reference: Optional[str] = None

class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    from_type: Optional[str]
    from_id: Optional[int]
    to_type: Optional[str]
    to_id: Optional[int]
    quantity: int
    movement_type: str
    reference: Optional[str]
    notes: Optional[str]
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
