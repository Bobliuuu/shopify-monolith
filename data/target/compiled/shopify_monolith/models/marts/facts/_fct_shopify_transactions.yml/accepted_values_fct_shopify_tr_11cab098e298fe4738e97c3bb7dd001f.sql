
    
    

with all_values as (

    select
        sales_channel as value_field,
        count(*) as n_records

    from "data"."fct"."fct_shopify_transactions"
    group by sales_channel

)

select *
from all_values
where value_field not in (
    'online','in_store'
)


