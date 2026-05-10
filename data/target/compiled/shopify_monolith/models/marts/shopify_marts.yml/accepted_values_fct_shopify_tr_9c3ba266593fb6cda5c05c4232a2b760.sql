
    
    

with all_values as (

    select
        transaction_recency as value_field,
        count(*) as n_records

    from "data"."fct"."fct_shopify_transactions"
    group by transaction_recency

)

select *
from all_values
where value_field not in (
    'recent','recent_month','older'
)


