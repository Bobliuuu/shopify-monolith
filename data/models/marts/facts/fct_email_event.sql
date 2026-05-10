{{ config(tags=['fact', 'core']) }}

select
    delivery_id,
    campaign_id,
    recipient_email,
    event_name,
    sent_at,
    opened_at,
    clicked_at,
    'customerio' as source_system,
    coalesce(ingestion_mode, 'synthetic') as ingestion_mode
from {{ source('customerio_raw', 'deliveries') }}
