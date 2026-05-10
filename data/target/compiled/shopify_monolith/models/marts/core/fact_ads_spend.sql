

select
    campaign_id,
    campaign_name,
    date,
    impressions,
    clicks,
    cost_micros / 1000000.0 as cost,
    conversions,
    'google_ads' as source_system,
    coalesce(ingestion_mode, 'synthetic') as ingestion_mode
from "data"."google_ads"."campaign_stats"