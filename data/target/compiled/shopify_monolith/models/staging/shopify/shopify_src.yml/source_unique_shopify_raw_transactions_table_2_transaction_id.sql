
    
    

select
    transaction_id as unique_field,
    count(*) as n_records

from "shopify_airflow"."public"."transactions_table_2"
where transaction_id is not null
group by transaction_id
having count(*) > 1


