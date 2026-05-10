{{ config(tags=['analytics_view']) }}

select * from {{ ref('fct_ga4_events') }}
