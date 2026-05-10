

select
    cast(id as varchar) as payment_key,
    cast(customer as varchar) as customer_key,
    cast(amount as double) / 100.0 as amount,
    currency,
    to_timestamp(created) as created_at,
    status,
    'stripe' as source_system,
    coalesce(ingestion_mode, 'live') as ingestion_mode
from "data"."stripe"."stripe_charges"