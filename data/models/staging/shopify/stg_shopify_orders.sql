-- Staging model for Shopify orders
-- Explicitly cast ID fields as VARCHAR to prevent dbt from converting to INT64

with source as (
    select * from {{ source('shopify_raw', 'shopify_orders') }}
),

staged as (
    select
        -- Explicitly cast all ID fields as VARCHAR
        cast(id as varchar) as id,
        
        -- Order fields
        name,
        email,
        phone,
        
        -- Timestamps
        created_at,
        updated_at,
        processed_at,
        cancelled_at,
        
        -- Order details
        cancel_reason,
        
        -- Pricing information (JSON fields)
        total_price_set,
        subtotal_price_set,
        total_tax_set,
        total_shipping_price_set,
        
        -- Customer information (JSON field)
        customer,
        
        -- Addresses (JSON fields)
        shipping_address,
        billing_address,
        
        -- Line items (JSON field with nested IDs)
        line_items,
        
        -- Metadata
        'shopify' as source_system,
        current_timestamp as dbt_loaded_at
    from source
)

select * from staged 