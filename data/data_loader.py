import sqlite3
import pandas as pd

def load_data():
    try:
        db_path = "E:/furni4/data/furniture_orders.db"
        print(f"ℹ️ Connecting to database: {db_path}")  # Debugging info
        
        conn = sqlite3.connect(db_path)
        print("✅ Connection successful!")  # Debugging info
        
        df = pd.read_sql("SELECT * FROM orders", conn)
        conn.close()

        if df.empty:
            print("❌ DataFrame is empty. No data retrieved from the database.")
        else:
            print("✅ Data loaded successfully!")
            print(df.head())  # Print first few rows for verification

        return df

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

# Run the function for testing
if __name__ == "__main__":
    load_data()
