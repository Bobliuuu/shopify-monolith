#!/usr/bin/env python3
"""
Script to display sample data from the shopify_transactions_base table
"""

import duckdb
import pandas as pd

def show_transactions_data():
    """Display sample data from the shopify_transactions_base table"""
    
    # Connect to the DuckDB database
    conn = duckdb.connect('shopify_monolith.duckdb')
    
    try:
        # Query the shopify_transactions_base table
        query = """
        SELECT 
            transaction_id,
            order_id,
            customer_id,
            transaction_status,
            payment_method,
            transaction_amount,
            tax_amount,
            shipping_amount,
            total_amount,
            successful_amount,
            currency,
            country_code,
            sales_channel,
            transaction_recency,
            created_at
        FROM main_dev.fct_shopify_transactions 
        LIMIT 10
        """
        
        # Execute query and get results
        result = conn.execute(query)
        df = result.fetchdf()
        
        print("Sample data from fct_shopify_transactions table:")
        print("=" * 80)
        print(df.to_string(index=False))
        print("\n" + "=" * 80)
        
        # Show some statistics
        stats_query = """
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(CASE WHEN transaction_status = 'completed' THEN 1 END) as completed_transactions,
            COUNT(CASE WHEN transaction_status = 'pending' THEN 1 END) as pending_transactions,
            COUNT(CASE WHEN transaction_status = 'failed' THEN 1 END) as failed_transactions,
            AVG(transaction_amount) as avg_transaction_amount,
            SUM(CASE WHEN transaction_status = 'completed' THEN transaction_amount ELSE 0 END) as total_successful_amount
        FROM main_dev.fct_shopify_transactions
        """
        
        stats_result = conn.execute(stats_query)
        stats_df = stats_result.fetchdf()
        
        print("\nTransaction Statistics:")
        print("=" * 40)
        for col in stats_df.columns:
            value = stats_df[col].iloc[0]
            if isinstance(value, float):
                print(f"{col}: {value:,.2f}")
            else:
                print(f"{col}: {value:,}")
                
    finally:
        conn.close()

if __name__ == "__main__":
    show_transactions_data() 