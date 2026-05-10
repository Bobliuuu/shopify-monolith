# Future: PostgreSQL + Debezium → DuckDB (optional)

The architecture diagram shows legacy data flowing **PostgreSQL → Debezium →** the warehouse. This repository does **not** yet implement CDC ingestion.

If prioritized:

1. Land Debezium change events (JSON) into object storage or Kafka.
2. Add an Airflow task or small loader that writes **append-only** staging tables in DuckDB under a schema such as `cdc` or `legacy_raw`.
3. Model CDC tables in dbt **staging** → **intermediate** (dedupe / merge) → **facts** with **incremental** materializations where appropriate.

Until then, use [`warehouse/legacy/csv_loader.py`](../../warehouse/legacy/csv_loader.py) and `legacy.*` stub tables for non-Shopify batch loads.
