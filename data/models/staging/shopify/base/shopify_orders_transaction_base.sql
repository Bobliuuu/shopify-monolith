-- shopify_order_transactions_base.sql
-- Base transactions table that pulls from source tables
-- References actual source tables from shopify_airflow database

with transactions_source_table as (
    select
        created_at,
        gift_card_details,
        id,
        kind,
        order_id,
        payment_details,
        payment_icon,
        processed_at,
        status,
        transaction_amount,
        transaction_parent_id,
        type,
        type_details
    from {{ source('shopify_order_transactions_table', 'order_transaction') }}
)

select *
from transactions_source_table
