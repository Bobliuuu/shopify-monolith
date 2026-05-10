{{ config(tags=['dimension', 'core']) }}

select distinct
    cast(campaign_id as varchar) as campaign_key,
    campaign_name,
    'google_ads' as source_system,
    coalesce(ingestion_mode, 'synthetic') as ingestion_mode
from {{ source('google_ads_raw', 'campaign_stats') }}
