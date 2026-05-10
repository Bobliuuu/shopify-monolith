

select
    event_date,
    event_name,
    user_pseudo_id,
    transaction_id,
    value,
    currency,
    page_location,
    'ga4' as source_system,
    coalesce(ingestion_mode, 'synthetic') as ingestion_mode
from "data"."ga4"."events"