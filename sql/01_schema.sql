-- Drop tables if they already exist to ensure a clean setup
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS stores;

-- 1. Master Data: Stores
CREATE TABLE stores (
    store_id INTEGER PRIMARY KEY,
    store_name TEXT NOT NULL,
    region TEXT NOT NULL,
    sales_area_sqm INTEGER NOT NULL
);

-- 2. Master Data: Products
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL, -- e.g., 'Fresh', 'Dry Goods', 'Beverages'
    shelf_life_days INTEGER NOT NULL,
    purchase_price REAL NOT NULL,
    retail_price REAL NOT NULL
);

-- 3. Transactional Data: Daily Inventory Levels
CREATE TABLE inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date DATE NOT NULL,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    current_stock INTEGER NOT NULL,
    reorder_point INTEGER NOT NULL,
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 4. Transactional Data: Daily Sales & Shrinkage (Spoilage)
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date DATE NOT NULL,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    units_sold INTEGER NOT NULL,
    shrinkage_units INTEGER NOT NULL, -- Discarded items due to expiration
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
