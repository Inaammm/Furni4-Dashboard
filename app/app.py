import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import os
import urllib.request

# Database Path Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "furniture_orders.db")
DB_GITHUB_URL = "https://raw.githubusercontent.com/Inaammm/Furni4-Dashboard/main/data/furniture_orders.db"

# Ensure database exists
if not os.path.exists(DB_PATH):
    try:
        urllib.request.urlretrieve(DB_GITHUB_URL, DB_PATH)
        print("✅ Database downloaded from GitHub.")
    except Exception as e:
        print(f"❌ Failed to download DB: {e}")

# Authentication Users
USERS = {
    "admin": "admin123",
    "vendor1": "password123",
    "vendor2": "password456"
}

def authenticate(username, password):
    return USERS.get(username) == password

def load_orders():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM orders", conn)
    conn.close()
    return df

def update_pending_balance(order_id, new_balance):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET pending_balance_fixed = ? WHERE id = ?", (new_balance, order_id))
    conn.commit()
    conn.close()

def add_order(order_date, customer_name, product_name, quantity, price, total_paid, pending_balance_fixed, total_paid_date):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (order_date, customer_name, product_name, quantity, price, total_paid, pending_balance_fixed, total_paid_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (order_date, customer_name, product_name, quantity, price, total_paid, pending_balance_fixed, total_paid_date))
    conn.commit()
    conn.close()

def clear_orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders;")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='orders';")
    conn.commit()
    conn.close()

def check_and_add_columns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(orders);")
    columns = [col[1] for col in cursor.fetchall()]
    if "total_paid_date" not in columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN total_paid_date INTEGER;")
    if "price" not in columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN price REAL NOT NULL DEFAULT 0;")
    conn.commit()
    conn.close()

check_and_add_columns()

# Streamlit Setup
st.set_page_config(page_title="Furni4 Sales Dashboard", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 Login to Furni4 Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {username}!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password!")
    st.stop()

st.title("📊 Furni4 Sales Dashboard")
df = load_orders()
if df.empty:
    st.warning("⚠️ No orders found.")
else:
    st.sidebar.header("🔍 Filter Orders")
    start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime(df["order_date"]).min().date())
    end_date = st.sidebar.date_input("End Date", value=pd.to_datetime(df["order_date"]).max().date())
    product_list = ["All"] + sorted(df["product_name"].unique().tolist())
    selected_product = st.sidebar.selectbox("Filter by Product", product_list)
    df["order_date"] = pd.to_datetime(df["order_date"])
    filtered_df = df[(df["order_date"] >= pd.Timestamp(start_date)) & (df["order_date"] <= pd.Timestamp(end_date))]
    if selected_product != "All":
        filtered_df = filtered_df[filtered_df["product_name"] == selected_product]
    st.subheader("📋 Order Data")
    st.dataframe(filtered_df)
    st.subheader("✏️ Pending Balance")
    order_ids = filtered_df["id"].tolist()
    if order_ids:
        selected_order = st.selectbox("Select Order ID", order_ids)
        new_balance = st.number_input("New Pending Balance", min_value=0.0, step=0.01)
        if st.button("Update Balance"):
            update_pending_balance(selected_order, new_balance)
            st.success(f"✅ Updated pending balance for Order ID {selected_order}")
            st.rerun()
    st.subheader("➕ Add New Order")
    order_date = st.date_input("Order Date", date.today())
    customer_name = st.text_input("Customer Name")
    product_name = st.text_input("Product Name")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    price = st.number_input("Price per Item", min_value=0.0, step=0.01)
    total_paid = st.number_input("Total Paid", min_value=0.0, step=0.01)
    pending_balance_fixed = st.number_input("Pending Balance", min_value=0.0, step=0.01)
    total_paid_date = st.date_input("Total Paid Date", date.today())
    total_paid_date_numeric = int(datetime.strptime(str(total_paid_date), "%Y-%m-%d").strftime("%Y%m%d"))
    if st.button("Add Order"):
        if customer_name and product_name and price > 0:
            add_order(order_date, customer_name, product_name, quantity, price, total_paid, pending_balance_fixed, total_paid_date_numeric)
            st.success("✅ Order added successfully!")
            st.rerun()
        else:
            st.error("⚠️ Please fill all required fields!")
    st.subheader("📊 Sales Overview")
    fig = px.bar(filtered_df, x="product_name", y="total_paid", title="Sales by Product")
    st.plotly_chart(fig)
    if st.session_state.username == "admin" and st.sidebar.button("🗑️ Clear All Orders"):
        clear_orders()
        st.warning("⚠️ All orders have been deleted!")
        st.rerun()
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
