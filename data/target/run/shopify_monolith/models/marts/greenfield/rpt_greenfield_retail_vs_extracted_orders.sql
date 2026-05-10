
  
  create view "data"."main"."rpt_greenfield_retail_vs_extracted_orders__dbt_tmp" as (
    -- Reconcile ground-truth retail orders with extracted_orders (same keys as generator).


with retail as (
    select * from "data"."greenfield"."retail_orders"
),

extracted as (
    select * from "data"."greenfield"."extracted_orders"
)

select
    r.order_id as retail_order_id,
    r.order_number,
    r.customer_id as retail_customer_id,
    r.source_tx_id,
    r.source_invoice_no,
    r.payment_ref as retail_payment_ref,
    r.grand_total as retail_grand_total,
    e.doc_id,
    e.extraction_id,
    e.grand_total as extracted_grand_total,
    abs(coalesce(e.grand_total, 0) - coalesce(r.grand_total, 0)) as grand_total_abs_diff
from retail r
left join extracted e
    on r.source_tx_id = e.source_tx_id
    and r.source_invoice_no = e.source_invoice_no
  );
