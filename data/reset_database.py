import sqlite3
import os
from datetime import datetime

db_path = "E:/furni4/data/furniture_orders.db"

# Ensure old database is deleted to avoid corruption issues
if os.path.exists(db_path):
    os.remove(db_path)
    print("🗑️ Deleted old corrupted database.")

# Create a new database connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the 'orders' table
cursor.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        total_paid REAL DEFAULT 0,
        order_date TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        pending_balance_fixed REAL DEFAULT 0,
        total_paid_date INTEGER DEFAULT 0  -- Stored as YYYYMMDD format
    )
''')

# Create the 'users' table for authentication (without bcrypt hashing)
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL  -- Plain text for now (not secure)
    )
''')

# Insert sample users (Vendor 1 & Vendor 2) - Plain text passwords for now
cursor.executemany('''
    INSERT INTO users (username, password) VALUES (?, ?)
''', [
    ('vendor1', 'password123'),  # Plain text password (for now)
    ('vendor2', 'securepass')
])

# Insert sample orders
cursor.executemany('''
    INSERT INTO orders (product_name, quantity, price, total_paid, order_date, customer_name, pending_balance_fixed, total_paid_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', [
    ('Chair', 5, 100.0, 400.0, '2025-03-07', 'John Doe', 100.0, int(datetime.strptime("2025-03-07", "%Y-%m-%d").strftime("%Y%m%d"))),
    ('Table', 2, 250.0, 500.0, '2025-03-06', 'Jane Smith', 0.0, int(datetime.strptime("2025-03-06", "%Y-%m-%d").strftime("%Y%m%d")))
])

conn.commit()
conn.close()

print("✅ Fresh database with user authentication and updated order fields created successfully!")
