-- Intermediate: normalized Stripe charge amounts and timestamps for facts.


select
    cast(id as varchar) as charge_id,
    cast(customer as varchar) as customer_id,
    cast(amount as double) / 100.0 as amount,
    lower(currency) as currency,
    epoch_ms(cast(created as bigint) * 1000) as created_at,
    status,
    coalesce(ingestion_mode, 'live') as ingestion_mode
from "data"."stripe"."stripe_charges"