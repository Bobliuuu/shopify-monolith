-- Intermediate: unify customer identifiers across Stripe and Customer.io before conformed dim.
{{ config(tags=['intermediate']) }}

with st as (
    select
        cast(id as varchar) as customer_key,
        email,
        'stripe' as source_system,
        coalesce(ingestion_mode, 'live') as ingestion_mode
    from {{ source('stripe_raw', 'stripe_customers') }}
),
cio as (
    select
        cio_id as customer_key,
        email,
        'customerio' as source_system,
        coalesce(ingestion_mode, 'synthetic') as ingestion_mode
    from {{ source('customerio_raw', 'profiles') }}
)
select * from st
union all by name
select * from cio
