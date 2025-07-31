"""
Airflow DAG for Shopify Products Data Ingestion

This DAG extracts product data from Shopify API and loads it into DuckDB.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
import json
import requests
import duckdb
import os
from typing import Dict, List, Any

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
    'shopify_products_ingestion',
    default_args=default_args,
    description='Extract Shopify products and load into DuckDB',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
    tags=['shopify', 'products', 'etl'],
)

def get_shopify_products(**context) -> List[Dict[str, Any]]:
    """
    Extract products from Shopify API
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
    
    products = []
    page_info = None
    
    while True:
        url = f"https://{shopify_domain}/admin/api/2024-01/products.json"
        params = {'limit': 250}  # Maximum allowed by Shopify
        
        if page_info:
            params['page_info'] = page_info
            
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        products.extend(data.get('products', []))
        
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
    context['task_instance'].xcom_push(key='products_data', value=products)
    return products

def transform_shopify_products(**context) -> List[Dict[str, Any]]:
    """
    Transform Shopify products data
    """
    products = context['task_instance'].xcom_pull(task_ids='extract_products', key='products_data')
    
    transformed_products = []
    
    for product in products:
        # Flatten and transform the product data
        transformed_product = {
            'id': product.get('id'),
            'title': product.get('title'),
            'body_html': product.get('body_html'),
            'vendor': product.get('vendor'),
            'product_type': product.get('product_type'),
            'created_at': product.get('created_at'),
            'handle': product.get('handle'),
            'updated_at': product.get('updated_at'),
            'published_at': product.get('published_at'),
            'template_suffix': product.get('template_suffix'),
            'status': product.get('status'),
            'published_scope': product.get('published_scope'),
            'admin_graphql_api_id': product.get('admin_graphql_api_id'),
            'tags': product.get('tags'),
            'total_inventory': product.get('total_inventory', 0),
            'total_variants': len(product.get('variants', [])),
            'total_images': len(product.get('images', [])),
            'total_options': len(product.get('options', [])),
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        # Add variant information
        variants = product.get('variants', [])
        for variant in variants:
            variant_data = transformed_product.copy()
            variant_data.update({
                'variant_id': variant.get('id'),
                'variant_title': variant.get('title'),
                'variant_sku': variant.get('sku'),
                'variant_price': variant.get('price'),
                'variant_compare_at_price': variant.get('compare_at_price'),
                'variant_inventory_quantity': variant.get('inventory_quantity'),
                'variant_inventory_management': variant.get('inventory_management'),
                'variant_inventory_policy': variant.get('inventory_policy'),
                'variant_fulfillment_service': variant.get('fulfillment_service'),
                'variant_taxable': variant.get('taxable'),
                'variant_barcode': variant.get('barcode'),
                'variant_grams': variant.get('grams'),
                'variant_weight': variant.get('weight'),
                'variant_weight_unit': variant.get('weight_unit'),
                'variant_requires_shipping': variant.get('requires_shipping'),
                'variant_tax_code': variant.get('tax_code'),
                'variant_position': variant.get('position'),
                'variant_option1': variant.get('option1'),
                'variant_option2': variant.get('option2'),
                'variant_option3': variant.get('option3'),
            })
            transformed_products.append(variant_data)
    
    # Push transformed data to XCom
    context['task_instance'].xcom_push(key='transformed_products', value=transformed_products)
    return transformed_products

def load_to_duckdb(**context):
    """
    Load transformed products data into DuckDB
    """
    import os
    
    transformed_products = context['task_instance'].xcom_pull(
        task_ids='transform_products', 
        key='transformed_products'
    )
    
    # Connect to DuckDB
    db_path = os.path.join(os.getcwd(), 'data', 'shopify_monolith.duckdb')
    conn = duckdb.connect(db_path)
    
    # Create table if not exists
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS shopify_products (
        id BIGINT,
        title VARCHAR,
        body_html TEXT,
        vendor VARCHAR,
        product_type VARCHAR,
        created_at TIMESTAMP,
        handle VARCHAR,
        updated_at TIMESTAMP,
        published_at TIMESTAMP,
        template_suffix VARCHAR,
        status VARCHAR,
        published_scope VARCHAR,
        admin_graphql_api_id VARCHAR,
        tags VARCHAR,
        total_inventory INTEGER,
        total_variants INTEGER,
        total_images INTEGER,
        total_options INTEGER,
        extraction_timestamp TIMESTAMP,
        variant_id BIGINT,
        variant_title VARCHAR,
        variant_sku VARCHAR,
        variant_price DECIMAL(10,2),
        variant_compare_at_price DECIMAL(10,2),
        variant_inventory_quantity INTEGER,
        variant_inventory_management VARCHAR,
        variant_inventory_policy VARCHAR,
        variant_fulfillment_service VARCHAR,
        variant_taxable BOOLEAN,
        variant_barcode VARCHAR,
        variant_grams INTEGER,
        variant_weight DECIMAL(10,2),
        variant_weight_unit VARCHAR,
        variant_requires_shipping BOOLEAN,
        variant_tax_code VARCHAR,
        variant_position INTEGER,
        variant_option1 VARCHAR,
        variant_option2 VARCHAR,
        variant_option3 VARCHAR
    )
    """
    
    conn.execute(create_table_sql)
    
    # Insert data
    if transformed_products:
        # Convert to DataFrame for easier insertion
        import pandas as pd
        df = pd.DataFrame(transformed_products)
        
        # Insert with replace to handle duplicates
        conn.execute("DELETE FROM shopify_products WHERE extraction_timestamp = ?", 
                    [transformed_products[0]['extraction_timestamp']])
        
        conn.execute("INSERT INTO shopify_products SELECT * FROM df")
    
    conn.close()
    print(f"Loaded {len(transformed_products)} product records to DuckDB")

# Task definitions
extract_task = PythonOperator(
    task_id='extract_products',
    python_callable=get_shopify_products,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_products',
    python_callable=transform_shopify_products,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_to_duckdb',
    python_callable=load_to_duckdb,
    dag=dag,
)

# Task dependencies
extract_task >> transform_task >> load_task 