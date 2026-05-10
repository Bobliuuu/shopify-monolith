{# Incremental fact for append-heavy GA4-shaped events #}
{{ config(
    materialized='incremental',
    unique_key='ga4_event_key',
    tags=['fact', 'core', 'incremental']
) }}

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
    from {{ source('ga4_raw', 'events') }}
)

select *
from src
{% if is_incremental() %}
where event_date > (select coalesce(max(event_date), '1970-01-01') from {{ this }})
{% endif %}
