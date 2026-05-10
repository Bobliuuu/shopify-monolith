# DuckDB + dbt layering conventions

This project maps **medallion-style** layers to DuckDB **schemas** (see `macros/generate_schema_name.sql` for unprefixed schema names).

## Layer definitions

| Layer | DuckDB schema | dbt folder | Prefix | Materialization | Purpose |
|-------|----------------|------------|--------|-----------------|---------|
| **Raw** | `shopify`, `stripe`, `ga4`, … | (sources only) | — | Tables from DLT / loaders | Vendor-faithful landing zones; do not reference in BI directly. |
| **Base** | `base` | `models/base/` | `base_*` optional | view/table | Light normalization over one source family (typing, column rename). |
| **Staging** | `staging` | `models/staging/` | `stg_*` | view | Atomic building blocks; one concept per model; joins rare. |
| **Intermediate** | `intermediate` | `models/intermediate/` | `int_*` | view | Business logic, unions across staging, prep for dims/facts. |
| **Dimensions** | `dim` | `models/marts/dimensions/` | `dim_*` | table | Conformed entities (customer, campaign, …). |
| **Facts** | `fct` | `models/marts/facts/` | `fct_*` | table / **incremental** | Measures & grains; append-heavy models use `materialized='incremental'`. |
| **Marts** | `mart` | `models/marts/greenfield/` (domain) | `rpt_*`, domain | view/table | Subject-area reporting (reconciliation, bridges). |
| **Analytics views** | `analytics_views` | `models/views/` | `vw_*` | view | Stable contracts for BI tools (thin wrappers over dims/facts/marts). |

## Incremental (`inc`)

Models that load **append-only** or **partitioned** data use dbt `incremental` (tagged `incremental` where applicable). Examples: event streams, charges. Not every fact is incremental.

## Views vs tables

- **Tables** (`dim`, `fct`): predictable performance for dashboards.
- **Views** (`staging`, `intermediate`, `analytics_views`): freshness and simplicity; BI should prefer **`analytics_views`** schema for stable column names.

## Connection to BI (direct DuckDB)

See [bi_direct_duckdb.md](bi_direct_duckdb.md). Prefer **`analytics_views`** (and curated **`dim`** / **`fct`**) over raw vendor schemas.
