{{ config(tags=['fact', 'core']) }}

select
    cast(external_order_id as varchar) as order_key,
    customer_email,
    order_total,
    currency,
    placed_at,
    'legacy' as source_system,
    coalesce(ingestion_mode, 'synthetic') as ingestion_mode
from {{ source('legacy_raw', 'orders_csv_stub') }}
