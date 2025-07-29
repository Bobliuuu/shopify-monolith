-- Base transactions table that pulls from source tables
-- References actual source tables from shopify_airflow database

with source_transactions_1 as (
    select 
        transaction_id,
        order_id,
        customer_id,
        transaction_status,
        payment_method,
        transaction_amount,
        tax_amount,
        shipping_amount,
        currency,
        created_at,
        updated_at,
        country_code,
        sales_channel,
        'transactions_table_1' as source_table
    from {{ source('shopify_raw', 'transactions_table_1') }}
),

source_transactions_2 as (
    select 
        transaction_id,
        order_id,
        customer_id,
        transaction_status,
        payment_method,
        transaction_amount,
        tax_amount,
        shipping_amount,
        currency,
        created_at,
        updated_at,
        country_code,
        sales_channel,
        'transactions_table_2' as source_table
    from {{ source('shopify_raw', 'transactions_table_2') }}
),

combined_base_transactions as (
    select * from source_transactions_1
    union all
    select * from source_transactions_2
)

select * from combined_base_transactions 