# Data Load Tool (DLT) Pipeline

DLT pipelines load API data into the **monolith DuckDB** at the repository root: **`data.duckdb`**.

Each pipeline uses:

- API authentication via environment variables (see `env.example`)
- Source definitions under `sources/`
- Dataset names map to **DuckDB schemas**: `shopify`, `stripe`, etc.

---

## Running Pipelines

Run from the `dlt/` directory so imports resolve (`python -m pipelines.<module>`).

### Shopify

**Command:**  
`python -m pipelines.run_shopify_pipeline`

**Destination:** `../data.duckdb`  
**Schema:** `shopify`  
**Tables:** `shopify_products` (and additional resources as you extend the source)

### Stripe

**Command:**  
`python -m pipelines.run_stripe_pipeline`

**Destination:** `../data.duckdb`  
**Schema:** `stripe`  
**Tables:** `stripe_customers`, `stripe_charges`, `stripe_invoices`

---

## Project Structure

```
├── pipelines/      # Entry points per integration
├── sources/        # DLT source definitions
├── env.example     # Environment variable template
```
