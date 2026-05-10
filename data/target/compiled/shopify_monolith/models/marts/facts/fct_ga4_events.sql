


with src as (
    select
        md5(
            concat_ws(
                '||',
                coalesce(cast(event_date as varchar), ''),
                coalesce(event_name, ''),
                coalesce(user_pseudo_id, ''),
                coalesce(cast(page_location as varchar), ''),
                coalesce(cast(value as varchar), '')
            )
        ) as ga4_event_key,
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
)

select *
from src
