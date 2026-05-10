-- Non-Shopify / legacy order rows (CSV exports, POS, etc.)


select
    cast(external_order_id as varchar) as order_key,
    customer_email,
    order_total,
    currency,
    placed_at,
    'legacy' as source_system,
    coalesce(ingestion_mode, 'synthetic') as ingestion_mode
from "data"."legacy"."orders_csv_stub"