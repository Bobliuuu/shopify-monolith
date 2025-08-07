-- Base transactions table that pulls from source tables
-- References actual source tables from shopify_airflow database


with customer_source_table as (
    select 
        created_at,
        customer_id,
        fist_name,
        last_name,
        phone_number,
        email_adress,
        total_spend,
        orders_count,
        customer_state
    from {{ source('shopify_customer', 'customers_table') }}
),

select * from customer_source_table 