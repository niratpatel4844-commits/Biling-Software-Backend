from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import auth, users, roles, companies, branches, franchises, warehouses, products, dashboard, customers, audit_logs

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    from app.seed import seed_default_data
    seed_default_data()


# Register routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(companies.router)
app.include_router(branches.router)
app.include_router(franchises.router)
app.include_router(warehouses.router)
app.include_router(products.router)
from app.routers import brands, units, product_variants, categories
app.include_router(categories.router)
app.include_router(brands.router)
app.include_router(units.router)
app.include_router(product_variants.router)
app.include_router(customers.router)
app.include_router(customers.vendor_router)
app.include_router(audit_logs.router)
from app.routers import inventory, sales, purchases
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(purchases.router)


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
