
    
    

with all_values as (

    select
        transaction_status as value_field,
        count(*) as n_records

    from "shopify_airflow"."public"."transactions_table_2"
    group by transaction_status

)

select *
from all_values
where value_field not in (
    'pending','completed','failed'
)


