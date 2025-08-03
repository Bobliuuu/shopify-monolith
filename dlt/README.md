# Data Load Tool (DLT) Pipeline

This repo contains **DLT-based pipelines** that extract data from APIs and loads it into a local Postgres database.

Each pipeline handles:
- API authentication
- Data extraction via DLT sources
- Loading into Postgres using inferred schemas

---

## Running Pipelines

To run a pipeline, execute the corresponding file in the `pipelines/` directory.

### Shopify

**Command:**  
`python pipelines/run_shopify_pipeline.py`

**Expected Tables:**
- `shopify_data__shopify_products`
- `shopify_data__shopify_orders`
- `shopify_data__shopify_customers`

### Stripe

**Command:**  
`python pipelines/run_stripe_pipeline.py`

**Expected Tables:**
- `stripe_data__stripe_customers`
- `stripe_data__stripe_charges`
- `stripe_data__stripe_invoices`

---

## Project Structure

```
├── pipelines/ # Entry points for each integration
├── sources/ # DLT source definitions per API
├── .env / env.example # Environment variable config
```