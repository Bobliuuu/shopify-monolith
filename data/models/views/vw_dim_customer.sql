-- Analytics view: stable contract for BI tools (Customer dimension).
{{ config(tags=['analytics_view']) }}

select * from {{ ref('dim_customer') }}
