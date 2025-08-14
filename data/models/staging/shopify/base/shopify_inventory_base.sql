-- Base transactions table that pulls from source tables
-- References actual source tables from shopify_airflow database


with inventory_source_table as (
    select 
        id,
        shopify_inventory_item_id,
        variant_id,
        sku,
        tracked,
        available_quantity,
        reserved_quantity,
        incoming_quantity,
        created_at,
        updated_at
    from {{ source('shopify_inventory_table', 'inventory_table') }}
),

select * from inventory_source_table 