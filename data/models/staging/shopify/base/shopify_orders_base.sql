-- Base transactions table that pulls from source tables
-- References actual source tables from shopify_airflow database


with orders_source_table as (
    select 
    id,
    legacy_resource_id,
    name,
    email,
    customer_id,
    processed_at,
    currency_code,
    financial_status,
    fulfillment_status,
    subtotal_price,
    total_price,
    total_tax,
    total_discounts,
    net_payment,
    cancelled_at,
    cancel_reason,
    closed_at,
    source_name,
    status_page_url,
    shipping_address,
    billing_address,
    tags,
    created_at,
    updated_at
    from {{ source('shopify_orders_table', 'orders_table') }}
),

select * from orders_source_table 