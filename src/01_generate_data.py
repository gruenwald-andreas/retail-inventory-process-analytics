import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Define project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "retail_warehouse.db"
SCHEMA_PATH = BASE_DIR / "sql" / "01_schema.sql"


def init_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    return conn


def populate_data(conn: sqlite3.Connection) -> None:
    np.random.seed(42)

    # 1. Insert store master data
    stores = pd.DataFrame([
        (1, "Store Regensburg-North", "Upper Palatinate", 850),
        (2, "Store Maxhuette-Haidhof", "Upper Palatinate", 920),
        (3, "Store Nuremberg-Center", "Middle Franconia", 1100),
        (4, "Store Munich-East", "Upper Bavaria", 1250),
        (5, "Store Landshut-South", "Lower Bavaria", 800)
    ], columns=["store_id", "store_name", "region", "sales_area_sqm"])
    stores.to_sql("stores", conn, if_exists="append", index=False)

    # 2. Insert product master data
    products = pd.DataFrame([
        (101, "Organic Whole Milk 1L", "Fresh", 7, 0.75, 1.19),
        (102, "Chicken Breast Fillet 400g", "Fresh", 4, 2.80, 4.49),
        (103, "Vine Tomatoes 500g", "Fresh", 5, 0.90, 1.79),
        (201, "Spaghetti 500g", "Dry Goods", 365, 0.45, 0.99),
        (202, "Coffee Beans Crema 1kg", "Dry Goods", 180, 6.50, 11.99),
        (301, "Mineral Water Classic 1.5L", "Beverages", 240, 0.15, 0.39)
    ], columns=["product_id", "product_name", "category", "shelf_life_days", "purchase_price", "retail_price"])
    products.to_sql("products", conn, if_exists="append", index=False)

    # 3. Generate 90 days of transactional data
    start_date = datetime(2026, 1, 1)
    inventory_rows = []
    sales_rows = []

    for day in range(90):
        current_date = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
        is_weekend = (start_date + timedelta(days=day)).weekday() >= 4

        for _, store in stores.iterrows():
            size_factor = store["sales_area_sqm"] / 900.0
            for _, prod in products.iterrows():
                reorder_point = int(20 * size_factor)

                # Simulated customer demand (higher on weekends)
                base_demand = np.random.poisson(12 * size_factor)
                demand = int(base_demand * (1.4 if is_weekend else 1.0))

                # Simulated stock level (including occasional supply shortages)
                if np.random.rand() < 0.08:
                    stock = 0  # Out-of-stock event
                else:
                    stock = max(0, int(np.random.normal(reorder_point * 1.5, 8)))

                units_sold = min(stock, demand)

                # Shrinkage occurs primarily in fresh produce
                if prod["category"] == "Fresh" and stock > units_sold:
                    shrinkage = np.random.binomial(stock - units_sold, 0.12)
                else:
                    shrinkage = 0

                inventory_rows.append((current_date, store["store_id"], prod["product_id"], stock, reorder_point))
                sales_rows.append((current_date, store["store_id"], prod["product_id"], units_sold, shrinkage))

    pd.DataFrame(
        inventory_rows,
        columns=["record_date", "store_id", "product_id", "current_stock", "reorder_point"]
    ).to_sql("inventory", conn, if_exists="append", index=False)

    pd.DataFrame(
        sales_rows,
        columns=["record_date", "store_id", "product_id", "units_sold", "shrinkage_units"]
    ).to_sql("sales", conn, if_exists="append", index=False)

    print(f"Database successfully created at: {DB_PATH}")


if __name__ == "__main__":
    connection = init_db()
    populate_data(connection)
    connection.close()
