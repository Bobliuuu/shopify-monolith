
    
    

with all_values as (

    select
        transaction_value_category as value_field,
        count(*) as n_records

    from "data"."fct"."fct_shopify_transactions"
    group by transaction_value_category

)

select *
from all_values
where value_field not in (
    'high_value','medium_value','low_value'
)


