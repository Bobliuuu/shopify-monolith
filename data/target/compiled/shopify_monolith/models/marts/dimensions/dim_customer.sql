-- Dimension: customers (conformed from intermediate identity spine).


select distinct
    customer_key,
    email,
    source_system,
    ingestion_mode
from "data"."intermediate"."int_customer_identity"