-- Base transactions table that pulls from source tables
-- References actual source tables from shopify_airflow database


with inventory_source_table as (
    select 
        inventory_item_id,
        available,
        location_id,
        updated_at
    from {{ source('shopify_inventory_table', 'inventory_table') }}
),

select * from inventory_source_table 