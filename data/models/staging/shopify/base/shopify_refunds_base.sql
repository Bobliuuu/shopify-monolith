-- shopify_refunds_base.sql
-- Base refunds table that pulls from source tables
-- References actual source tables from shopify_airflow database

with refunds_source_table as (
    select
        id,
        created_at,
        duties,
        legacy_resource_id,
        note,
        order_id,
        order_adjustments,
        refund_line_items,
        refund_shipping_lines,
        return_id,
        staff_member_id,
        total_refunded_set,
        transactions,
        updated_at
    from {{ source('shopify_refunds_table', 'refund') }}
)

select * 
from refunds_source_table