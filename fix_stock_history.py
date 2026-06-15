from app.database import engine, Base
from app.models.inventory import StockHistory

def recreate_stock_history():
    print("Dropping StockHistory table...")
    StockHistory.__table__.drop(engine, checkfirst=True)
    print("Recreating StockHistory table with new columns...")
    Base.metadata.create_all(engine)
    print("Done!")

if __name__ == "__main__":
    recreate_stock_history()
