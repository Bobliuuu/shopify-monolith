
  
  create view "data"."main"."dim_customer__dbt_tmp" as (
    -- Conformed customers from payments (Stripe) + email platform (Customer.io)


with st as (
    select
        cast(id as varchar) as customer_key,
        email,
        'stripe' as source_system,
        coalesce(ingestion_mode, 'live') as ingestion_mode
    from "data"."stripe"."stripe_customers"
),
cio as (
    select
        cio_id as customer_key,
        email,
        'customerio' as source_system,
        coalesce(ingestion_mode, 'synthetic') as ingestion_mode
    from "data"."customerio"."profiles"
)
select * from st
union all by name
select * from cio
  );
