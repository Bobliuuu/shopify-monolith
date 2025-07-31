#!/usr/bin/env python3
"""
Test script to verify Shopify API connectivity and data extraction
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_shopify_connection():
    """Test Shopify API connection and basic data extraction"""
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    shopify_domain = os.getenv('SHOPIFY_DOMAIN')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    
    if not shopify_domain or not access_token:
        print("❌ Error: SHOPIFY_DOMAIN and SHOPIFY_ACCESS_TOKEN must be set in .env file")
        return False
    
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    print(f"🔗 Testing connection to Shopify domain: {shopify_domain}")
    
    try:
        # Test products endpoint
        products_url = f"https://{shopify_domain}/admin/api/2024-01/products.json"
        response = requests.get(products_url, headers=headers, params={'limit': 5})
        response.raise_for_status()
        
        products_data = response.json()
        products_count = len(products_data.get('products', []))
        
        print(f"✅ Products API: Successfully retrieved {products_count} products")
        
        # Test orders endpoint
        orders_url = f"https://{shopify_domain}/admin/api/2024-01/orders.json"
        response = requests.get(orders_url, headers=headers, params={'limit': 5})
        response.raise_for_status()
        
        orders_data = response.json()
        orders_count = len(orders_data.get('orders', []))
        
        print(f"✅ Orders API: Successfully retrieved {orders_count} orders")
        
        # Show sample data structure
        if products_data.get('products'):
            sample_product = products_data['products'][0]
            print(f"\n📋 Sample product structure:")
            print(f"  - ID: {sample_product.get('id')}")
            print(f"  - Title: {sample_product.get('title')}")
            print(f"  - Vendor: {sample_product.get('vendor')}")
            print(f"  - Variants: {len(sample_product.get('variants', []))}")
        
        if orders_data.get('orders'):
            sample_order = orders_data['orders'][0]
            print(f"\n📋 Sample order structure:")
            print(f"  - ID: {sample_order.get('id')}")
            print(f"  - Name: {sample_order.get('name')}")
            print(f"  - Total Price: {sample_order.get('total_price')}")
            print(f"  - Line Items: {len(sample_order.get('line_items', []))}")
        
        print(f"\n🎉 All tests passed! Your Shopify API connection is working correctly.")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_duckdb_connection():
    """Test DuckDB connection and table creation"""
    
    try:
        import duckdb
        
        # Connect to DuckDB
        db_path = os.path.join(os.getcwd(), '..', 'data', 'shopify_monolith.duckdb')
        conn = duckdb.connect(db_path)
        
        # Test table creation
        create_test_sql = """
        CREATE TABLE IF NOT EXISTS test_connection (
            id INTEGER,
            test_column VARCHAR
        )
        """
        conn.execute(create_test_sql)
        
        # Test insert and select
        conn.execute("INSERT INTO test_connection VALUES (1, 'test')")
        result = conn.execute("SELECT * FROM test_connection").fetchall()
        
        # Cleanup
        conn.execute("DROP TABLE test_connection")
        conn.close()
        
        print(f"✅ DuckDB: Successfully connected and tested table operations")
        return True
        
    except Exception as e:
        print(f"❌ DuckDB Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Shopify Pipeline Setup\n")
    
    # Test Shopify API
    shopify_ok = test_shopify_connection()
    
    print("\n" + "="*50 + "\n")
    
    # Test DuckDB
    duckdb_ok = test_duckdb_connection()
    
    print("\n" + "="*50 + "\n")
    
    if shopify_ok and duckdb_ok:
        print("🎉 All tests passed! Your pipeline is ready to run.")
        print("\nNext steps:")
        print("1. Start Airflow: airflow webserver --port 8080")
        print("2. Start Scheduler: airflow scheduler")
        print("3. Access UI: http://localhost:8080")
    else:
        print("❌ Some tests failed. Please check your configuration.") 