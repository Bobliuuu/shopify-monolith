# Direct DuckDB connections for BI and activation

The analytical warehouse is **`data.duckdb`** at the repository root (override with `DBT_DUCKDB_PATH` when running dbt from `data/`).

Prefer schemas **`analytics_views`** (stable `vw_*` models), then **`dim`** / **`fct`** / **`mart`**, not raw vendor schemas (`shopify`, `stripe`, …) for end-user SQL.

## Connection basics

| Mechanism | Notes |
|-----------|------|
| **File path** | Point tools at the `.duckdb` file path (local or shared mount). |
| **MotherDuck** | HTTPS endpoint when using MotherDuck instead of a local file. |
| **ODBC / JDBC** | Use DuckDB’s ODBC/JDBC drivers where the tool supports custom SQL warehouses. |
| **Python** | `duckdb.connect(path)` / SQLAlchemy with duckdb-engine for Redash/Grafana plugins that run Python. |

## Tool-specific guidance

| Tool | Guidance |
|------|----------|
| **Grafana** | Use a SQL data source that can attach DuckDB (community plugins vary) or query via a small API/bridge that runs DuckDB. |
| **Redash** | Often DuckDB via Python query runner or JDBC if available in your Redash build. |
| **Tableau** | OD BC to DuckDB, or extract Parquet/CSV produced by scheduled exports from `vw_*` / `fct_*` models. |
| **Looker** | Requires a supported dialect; confirm your Looker edition. If unsupported, use semantic views exported to Parquet or a supported warehouse. |
| **Hightouch** | Use a Hightouch **source** that supports DuckDB if offered; otherwise schedule extracts from `analytics_views` into a supported intermediate store. |

## dbt lineage

Use **`dbt docs generate`** and **`exposures`** ([`models/exposures.yml`](../models/exposures.yml)) to track which models feed dashboards.
