-- shopify_products_base.sql
-- Base products table that pulls from source tables
-- References actual source tables from shopify_airflow database

with products_source_table as (
    select
        id,
        bundle_components,
        category,
        collections,
        combined_listing,
        combined_listing_role,
        compare_at_price_range,
        contextual_pricing,
        created_at,
        default_cursor,
        description,
        description_html,
        events,
        featured_media,
        feedback,
        gift_card_template_suffix,
        handle,
        has_only_default_variant,
        has_out_of_stock_variants,
        has_variants_that_requires_components,
        in_collection,
        is_gift_card,
        legacy_resource_id,
        media,
        media_count,
        metafield,
        metafields,
        online_store_preview_url,
        online_store_url,
        options,
        price_range_v2,
        product_components,
        product_components_count,
        product_parents,
        product_type,
        published_at,
        published_on_publication,
        requires_selling_plan,
        restricted_for_resource,
        selling_plan_groups,
        selling_plan_groups_count,
        seo,
        status,
        tags,
        template_suffix,
        title,
        total_inventory,
        tracks_inventory,
        translations,
        updated_at,
        variants,
        variants_count,
        vendor
    from {{ source('shopify_products_table', 'products_table') }}
)

select * 
from products_source_table
