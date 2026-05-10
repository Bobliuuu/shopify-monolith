-- Dimension: customers (conformed from intermediate identity spine).
{{ config(tags=['dimension', 'core']) }}

select distinct
    customer_key,
    email,
    source_system,
    ingestion_mode
from {{ ref('int_customer_identity') }}
