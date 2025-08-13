-- Staging model for Shopify customers
-- Explicitly cast ID fields as VARCHAR to prevent dbt from converting to INT64

with source as (
    select * from {{ source('shopify_raw', 'shopify_customers') }}
),

staged as (
    select
        -- Explicitly cast all ID fields as VARCHAR
        cast(id as varchar) as id,
        
        -- Customer fields
        first_name,
        last_name,
        email,
        phone,
        accepts_marketing,
        
        -- Timestamps
        created_at,
        updated_at,
        
        -- Customer metrics
        orders_count,
        total_spent,
        
        -- Customer details
        note,
        tags,
        
        -- Addresses (JSON fields)
        default_address,
        addresses,
        
        -- Metadata
        'shopify' as source_system,
        current_timestamp as dbt_loaded_at
    from source
)

select * from staged 