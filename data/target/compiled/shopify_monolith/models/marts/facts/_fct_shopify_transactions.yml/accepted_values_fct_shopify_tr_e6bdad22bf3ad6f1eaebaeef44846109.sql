
    
    

with all_values as (

    select
        payment_category as value_field,
        count(*) as n_records

    from "data"."fct"."fct_shopify_transactions"
    group by payment_category

)

select *
from all_values
where value_field not in (
    'card','digital_wallet','shop_pay'
)


