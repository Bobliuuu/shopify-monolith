
  
  create view "data"."main"."rpt_greenfield_product_skus_bridge__dbt_tmp" as (
    -- Bridge retail SKUs to Shopify-staged products when both exist (SKU embedded in variants JSON).


with retail_skus as (
    select distinct sku, name, product_id, variant_id
    from "data"."greenfield"."retail_products"
)

select
    rs.sku as greenfield_retail_sku,
    rs.name as greenfield_product_name,
    rs.product_id as greenfield_product_id,
    sp.id as shopify_product_row_id,
    sp.title as shopify_product_title,
    sp.vendor as shopify_vendor,
    case
        when sp.variants is null then false
        else strpos(cast(sp.variants as varchar), rs.sku) > 0
    end as sku_found_in_shopify_variants_json
from retail_skus rs
left join "data"."shopify"."shopify_products" sp
    on strpos(cast(sp.variants as varchar), rs.sku) > 0
  );
