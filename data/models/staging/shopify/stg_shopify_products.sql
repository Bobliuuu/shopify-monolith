-- Staging model for Shopify products
-- Explicitly cast ID fields as VARCHAR to prevent dbt from converting to INT64

with source as (
    select * from {{ source('shopify_raw', 'shopify_products') }}
),

staged as (
    select
        -- Explicitly cast all ID fields as VARCHAR
        cast(id as varchar) as id,
        cast(admin_graphql_api_id as varchar) as admin_graphql_api_id,
        
        -- Product fields
        title,
        body_html,
        vendor,
        product_type,
        handle,
        template_suffix,
        published_scope,
        tags,
        status,
        
        -- Timestamps
        created_at,
        updated_at,
        published_at,
        
        -- Options (JSON field)
        options,
        
        -- Variants (JSON field with nested IDs)
        variants,
        
        -- Images (JSON field with nested IDs)
        images,
        
        -- Featured image (JSON field)
        featured_image,
        
        -- Metadata
        'shopify' as source_system,
        current_timestamp as dbt_loaded_at
    from source
)

select * from staged 