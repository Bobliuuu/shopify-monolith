

select
    charge_id as payment_key,
    customer_id as customer_key,
    amount,
    currency,
    created_at,
    status,
    'stripe' as source_system,
    ingestion_mode
from "data"."intermediate"."int_stripe_charges"