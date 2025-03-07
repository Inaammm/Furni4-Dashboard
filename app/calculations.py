import pandas as pd

def calculate_metrics(df):
    """Calculate key metrics from the orders DataFrame."""
    total_sales = df['sales'].sum()
    total_orders = len(df)
    pending_orders = df[df['status'] == 'Pending'].shape[0]
    
    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "pending_orders": pending_orders
    }
