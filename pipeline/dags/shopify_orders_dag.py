"""
Airflow DAG for Shopify Orders Data Ingestion

This DAG extracts order data from Shopify API and loads it into DuckDB.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import duckdb
import os
from typing import Dict, List, Any
import json

# Default arguments for the DAG
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'shopify_orders_ingestion',
    default_args=default_args,
    description='Extract Shopify orders and load into DuckDB',
    schedule_interval='0 3 * * *',  # Daily at 3 AM
    catchup=False,
    tags=['shopify', 'orders', 'etl'],
)

def get_shopify_orders(**context) -> List[Dict[str, Any]]:
    """
    Extract orders from Shopify API
    """
    import os
    
    # Get Shopify credentials from environment variables
    shopify_domain = os.getenv('SHOPIFY_DOMAIN')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    
    if not shopify_domain or not access_token:
        raise ValueError("SHOPIFY_DOMAIN and SHOPIFY_ACCESS_TOKEN must be set")
    
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    orders = []
    page_info = None
    
    while True:
        url = f"https://{shopify_domain}/admin/api/2024-01/orders.json"
        params = {
            'limit': 250,  # Maximum allowed by Shopify
            'status': 'any'  # Include all order statuses
        }
        
        if test: 
            data = generate_test_data(schema, type, examples).data
        else: 
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

        if page_info:
            params['page_info'] = page_info
            
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        orders.extend(data.get('orders', []))
        
        # Check for next page
        link_header = response.headers.get('Link', '')
        if 'rel="next"' not in link_header:
            break
            
        # Extract page_info from Link header
        import re
        next_match = re.search(r'<[^>]*page_info=([^&>]+)[^>]*>; rel="next"', link_header)
        if next_match:
            page_info = next_match.group(1)
        else:
            break
    
    # Push to XCom for next task
    context['task_instance'].xcom_push(key='orders_data', value=orders)
    return orders

def transform_shopify_orders(**context) -> List[Dict[str, Any]]:
    """
    Transform Shopify orders data
    """
    orders = context['task_instance'].xcom_pull(task_ids='extract_orders', key='orders_data')
    
    transformed_orders = []
    
    for order in orders:
        # Flatten and transform the order data
        transformed_order = {
            'id': order.get('id'),
            'name': order.get('name'),
            'email': order.get('email'),
            'phone': order.get('phone'),
            'created_at': order.get('created_at'),
            'updated_at': order.get('updated_at'),
            'processed_at': order.get('processed_at'),
            'cancelled_at': order.get('cancelled_at'),
            'cancel_reason': order.get('cancel_reason'),
            'closed_at': order.get('closed_at'),
            'number': order.get('number'),
            'note': order.get('note'),
            'token': order.get('token'),
            'total_price': order.get('total_price'),
            'subtotal_price': order.get('subtotal_price'),
            'total_tax': order.get('total_tax'),
            'currency': order.get('currency'),
            'financial_status': order.get('financial_status'),
            'confirmed': order.get('confirmed'),
            'total_discounts': order.get('total_discounts'),
            'total_line_items_price': order.get('total_line_items_price'),
            'cart_token': order.get('cart_token'),
            'buyer_accepts_marketing': order.get('buyer_accepts_marketing'),
            'name': order.get('name'),
            'referring_site': order.get('referring_site'),
            'landing_site': order.get('landing_site'),
            'cancelled_at': order.get('cancelled_at'),
            'cancel_reason': order.get('cancel_reason'),
            'total_weight': order.get('total_weight'),
            'total_tip_received': order.get('total_tip_received'),
            'admin_graphql_api_id': order.get('admin_graphql_api_id'),
            'checkout_id': order.get('checkout_id'),
            'checkout_token': order.get('checkout_token'),
            'client_details': json.dumps(order.get('client_details', {})),
            'shipping_lines': json.dumps(order.get('shipping_lines', [])),
            'billing_address': json.dumps(order.get('billing_address', {})),
            'shipping_address': json.dumps(order.get('shipping_address', {})),
            'fulfillments': json.dumps(order.get('fulfillments', [])),
            'customer': json.dumps(order.get('customer', {})),
            'total_line_items': len(order.get('line_items', [])),
            'total_fulfillments': len(order.get('fulfillments', [])),
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        # Add line items information
        line_items = order.get('line_items', [])
        for line_item in line_items:
            line_item_data = transformed_order.copy()
            line_item_data.update({
                'line_item_id': line_item.get('id'),
                'line_item_variant_id': line_item.get('variant_id'),
                'line_item_title': line_item.get('title'),
                'line_item_quantity': line_item.get('quantity'),
                'line_item_sku': line_item.get('sku'),
                'line_item_variant_title': line_item.get('variant_title'),
                'line_item_vendor': line_item.get('vendor'),
                'line_item_fulfillment_service': line_item.get('fulfillment_service'),
                'line_item_product_id': line_item.get('product_id'),
                'line_item_requires_shipping': line_item.get('requires_shipping'),
                'line_item_taxable': line_item.get('taxable'),
                'line_item_gift_card': line_item.get('gift_card'),
                'line_item_name': line_item.get('name'),
                'line_item_variant_inventory_management': line_item.get('variant_inventory_management'),
                'line_item_properties': json.dumps(line_item.get('properties', [])),
                'line_item_product_exists': line_item.get('product_exists'),
                'line_item_fulfillable_quantity': line_item.get('fulfillable_quantity'),
                'line_item_grams': line_item.get('grams'),
                'line_item_price': line_item.get('price'),
                'line_item_total_discount': line_item.get('total_discount'),
                'line_item_fulfillment_status': line_item.get('fulfillment_status'),
                'line_item_price_set': json.dumps(line_item.get('price_set', {})),
                'line_item_total_discount_set': json.dumps(line_item.get('total_discount_set', {})),
                'line_item_discount_allocations': json.dumps(line_item.get('discount_allocations', [])),
                'line_item_tax_lines': json.dumps(line_item.get('tax_lines', [])),
            })
            transformed_orders.append(line_item_data)
    
    # Push transformed data to XCom
    context['task_instance'].xcom_push(key='transformed_orders', value=transformed_orders)
    return transformed_orders

def load_orders_to_duckdb(**context):
    """
    Load transformed orders data into DuckDB
    """
    import os
    
    transformed_orders = context['task_instance'].xcom_pull(
        task_ids='transform_orders', 
        key='transformed_orders'
    )
    
    # Connect to DuckDB
    db_path = os.path.join(os.getcwd(), 'data', 'shopify_monolith.duckdb')
    conn = duckdb.connect(db_path)
    
    # Create table if not exists
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS shopify_orders (
        id BIGINT,
        name VARCHAR,
        email VARCHAR,
        phone VARCHAR,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        processed_at TIMESTAMP,
        cancelled_at TIMESTAMP,
        cancel_reason VARCHAR,
        closed_at TIMESTAMP,
        number INTEGER,
        note TEXT,
        token VARCHAR,
        total_price DECIMAL(10,2),
        subtotal_price DECIMAL(10,2),
        total_tax DECIMAL(10,2),
        currency VARCHAR,
        financial_status VARCHAR,
        confirmed BOOLEAN,
        total_discounts DECIMAL(10,2),
        total_line_items_price DECIMAL(10,2),
        cart_token VARCHAR,
        buyer_accepts_marketing BOOLEAN,
        referring_site VARCHAR,
        landing_site VARCHAR,
        total_weight INTEGER,
        total_tip_received DECIMAL(10,2),
        admin_graphql_api_id VARCHAR,
        checkout_id BIGINT,
        checkout_token VARCHAR,
        client_details TEXT,
        shipping_lines TEXT,
        billing_address TEXT,
        shipping_address TEXT,
        fulfillments TEXT,
        customer TEXT,
        total_line_items INTEGER,
        total_fulfillments INTEGER,
        extraction_timestamp TIMESTAMP,
        line_item_id BIGINT,
        line_item_variant_id BIGINT,
        line_item_title VARCHAR,
        line_item_quantity INTEGER,
        line_item_sku VARCHAR,
        line_item_variant_title VARCHAR,
        line_item_vendor VARCHAR,
        line_item_fulfillment_service VARCHAR,
        line_item_product_id BIGINT,
        line_item_requires_shipping BOOLEAN,
        line_item_taxable BOOLEAN,
        line_item_gift_card BOOLEAN,
        line_item_name VARCHAR,
        line_item_variant_inventory_management VARCHAR,
        line_item_properties TEXT,
        line_item_product_exists BOOLEAN,
        line_item_fulfillable_quantity INTEGER,
        line_item_grams INTEGER,
        line_item_price DECIMAL(10,2),
        line_item_total_discount DECIMAL(10,2),
        line_item_fulfillment_status VARCHAR,
        line_item_price_set TEXT,
        line_item_total_discount_set TEXT,
        line_item_discount_allocations TEXT,
        line_item_tax_lines TEXT
    )
    """
    
    conn.execute(create_table_sql)
    
    # Insert data
    if transformed_orders:
        # Convert to DataFrame for easier insertion
        import pandas as pd
        df = pd.DataFrame(transformed_orders)
        
        # Insert with replace to handle duplicates
        conn.execute("DELETE FROM shopify_orders WHERE extraction_timestamp = ?", 
                    [transformed_orders[0]['extraction_timestamp']])
        
        conn.execute("INSERT INTO shopify_orders SELECT * FROM df")
    
    conn.close()
    print(f"Loaded {len(transformed_orders)} order records to DuckDB")

# Task definitions
extract_task = PythonOperator(
    task_id='extract_orders',
    python_callable=get_shopify_orders,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_orders',
    python_callable=transform_shopify_orders,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_orders_to_duckdb',
    python_callable=load_orders_to_duckdb,
    dag=dag,
)

# Task dependencies
extract_task >> transform_task >> load_task 