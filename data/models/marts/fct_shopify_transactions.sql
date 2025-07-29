-- Fact table for Shopify transactions with calculated fields
-- References the base table from staging/shopify/base

select 
  transaction_id,
  order_id,
  customer_id,
  transaction_status,
  payment_method,
  transaction_amount,
  tax_amount,
  shipping_amount,
  currency,
  created_at,
  updated_at,
  country_code,
  sales_channel,
  source_table,
  -- Add some calculated fields
  transaction_amount + tax_amount + shipping_amount as total_amount,
  case 
    when transaction_status = 'completed' then transaction_amount
    else 0
  end as successful_amount,
  case 
    when created_at >= current_timestamp - interval '7 days' then 'recent'
    when created_at >= current_timestamp - interval '30 days' then 'recent_month'
    else 'older'
  end as transaction_recency,
  -- Additional business logic
  case 
    when transaction_amount >= 1000 then 'high_value'
    when transaction_amount >= 500 then 'medium_value'
    else 'low_value'
  end as transaction_value_category,
  case 
    when payment_method = 'credit_card' then 'card'
    when payment_method = 'paypal' then 'digital_wallet'
    else 'shop_pay'
  end as payment_category
from {{ ref('shopify_transactions_base') }} 