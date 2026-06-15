from app.database import init_db
from app.models.customer_payment import CustomerPayment
from app.models.vendor_payment import VendorPayment
from app.models.delivery_challan import DeliveryChallan, DeliveryChallanItem
print("Initializing database...")
init_db()
print("Database initialization complete.")
