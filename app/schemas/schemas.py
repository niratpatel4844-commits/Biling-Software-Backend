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

class RoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class RoleResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    is_system: bool
    is_active: bool
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
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    capacity: Optional[str] = None

class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class WarehouseResponse(BaseModel):
    id: int
    name: str
    code: str
    company_id: int
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
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
    brand: Optional[str] = None
    unit: Optional[str] = "PCS"
    gst_percent: Optional[float] = 18
    hsn_code: Optional[str] = None
    cost_price: float
    selling_price: float
    mrp: Optional[float] = None
    min_stock: Optional[int] = 10
    company_id: Optional[int] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    gst_percent: Optional[float] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    mrp: Optional[float] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    unit: Optional[str] = None
    gst_percent: Optional[float] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    mrp: Optional[float] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Category ---
class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = 0

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None
    level: int
    is_active: bool

    class Config:
        from_attributes = True


# --- Customer ---
class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    gst_number: Optional[str] = None
    credit_limit: Optional[float] = 0
    company_id: Optional[int] = None

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    city: Optional[str] = None
    outstanding_amount: Optional[float] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Vendor ---
class VendorCreate(BaseModel):
    name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    company_id: Optional[int] = None

class VendorResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    outstanding_amount: Optional[float] = None
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
