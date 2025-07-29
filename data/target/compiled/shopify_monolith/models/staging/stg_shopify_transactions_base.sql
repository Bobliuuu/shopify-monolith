-- Staging model that combines multiple base tables
-- Currently testing with self-union, but designed to union different source tables
-- In production, this would reference actual source tables like:
-- from source('shopify_raw', 'transactions_table_1')

with base_table_1 as (
    select 
        'TXN_' || cast(row_number() over () as varchar) as transaction_id,
        'ORD_' || cast(row_number() over () as varchar) as order_id,
        'CUST_' || cast(row_number() over () as varchar) as customer_id,
        case 
            when random() < 0.3 then 'pending'
            when random() < 0.6 then 'completed'
            else 'failed'
        end as transaction_status,
        case 
            when random() < 0.4 then 'credit_card'
            when random() < 0.7 then 'paypal'
            else 'shop_pay'
        end as payment_method,
        round(random() * 1000 + 10, 2) as transaction_amount,
        round(random() * 50 + 5, 2) as tax_amount,
        round(random() * 20 + 2, 2) as shipping_amount,
        'USD' as currency,
        current_timestamp - interval '1 day' * random() * 30 as created_at,
        current_timestamp - interval '1 day' * random() * 30 as updated_at,
        case 
            when random() < 0.8 then 'US'
            when random() < 0.9 then 'CA'
            else 'UK'
        end as country_code,
        case 
            when random() < 0.7 then 'online'
            else 'in_store'
        end as sales_channel,
        'table_1' as source_table
    from range(1, 500)
),

base_table_2 as (
    select 
        'TXN_' || cast(row_number() over () + 500 as varchar) as transaction_id,
        'ORD_' || cast(row_number() over () + 500 as varchar) as order_id,
        'CUST_' || cast(row_number() over () + 500 as varchar) as customer_id,
        case 
            when random() < 0.3 then 'pending'
            when random() < 0.6 then 'completed'
            else 'failed'
        end as transaction_status,
        case 
            when random() < 0.4 then 'credit_card'
            when random() < 0.7 then 'paypal'
            else 'shop_pay'
        end as payment_method,
        round(random() * 1000 + 10, 2) as transaction_amount,
        round(random() * 50 + 5, 2) as tax_amount,
        round(random() * 20 + 2, 2) as shipping_amount,
        'USD' as currency,
        current_timestamp - interval '1 day' * random() * 30 as created_at,
        current_timestamp - interval '1 day' * random() * 30 as updated_at,
        case 
            when random() < 0.8 then 'US'
            when random() < 0.9 then 'CA'
            else 'UK'
        end as country_code,
        case 
            when random() < 0.7 then 'online'
            else 'in_store'
        end as sales_channel,
        'table_2' as source_table
    from range(1, 500)
),

combined_base as (
    select * from base_table_1
    union all
    select * from base_table_2
)

select * from combined_base