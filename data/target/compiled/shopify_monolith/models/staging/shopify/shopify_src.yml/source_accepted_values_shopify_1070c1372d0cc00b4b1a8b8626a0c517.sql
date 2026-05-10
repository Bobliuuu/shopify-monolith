
    
    

with all_values as (

    select
        sales_channel as value_field,
        count(*) as n_records

    from "shopify_airflow"."public"."transactions_table_1"
    group by sales_channel

)

select *
from all_values
where value_field not in (
    'online','in_store'
)


