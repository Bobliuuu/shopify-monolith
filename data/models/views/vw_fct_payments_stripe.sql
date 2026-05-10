{{ config(tags=['analytics_view']) }}

select * from {{ ref('fct_stripe_payment') }}
