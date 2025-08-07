-- Base transactions table that pulls from source tables
-- References actual source tables from shopify_airflow database


with orders_source_table as (
    select 
        order_id,
        created_at,
        total_price,
        currency,
        fulfillment_status,
        customer_id,
        shipping_address
    from {{ source('shopify_orders_table', 'orders_table') }}
),

select * from orders_source_table 