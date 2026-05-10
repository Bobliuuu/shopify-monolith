
  
  create view "data"."main"."dim_campaign__dbt_tmp" as (
    

select distinct
    cast(campaign_id as varchar) as campaign_key,
    campaign_name,
    'google_ads' as source_system,
    coalesce(ingestion_mode, 'synthetic') as ingestion_mode
from "data"."google_ads"."campaign_stats"
  );
