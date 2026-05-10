from pathlib import Path

import duckdb

_SCHEMA_SQL = Path(__file__).resolve().parent / "sql" / "schema.sql"


def apply_greenfield_schema(con: duckdb.DuckDBPyConnection) -> None:
    """Create greenfield schema and core tables if not present."""
    sql = _SCHEMA_SQL.read_text(encoding="utf-8")
    con.execute(sql)


def ensure_shopify_reconcile_stub_tables(con: duckdb.DuckDBPyConnection) -> None:
    """
    Ensure ``shopify.shopify_products`` (and peers) exist so dbt can join before DLT loads data.

    Safe no-op when DLT has already created real tables with compatible columns.
    """
    con.execute("CREATE SCHEMA IF NOT EXISTS shopify")
    # Minimal columns aligned with dlt/sources/shopify_source.py + stg_shopify_products
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS shopify.shopify_products (
            id VARCHAR,
            title VARCHAR,
            body_html VARCHAR,
            vendor VARCHAR,
            product_type VARCHAR,
            handle VARCHAR,
            status VARCHAR,
            tags VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            published_at TIMESTAMP,
            template_suffix VARCHAR,
            featured_image JSON,
            variants JSON,
            images JSON,
            options JSON
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS shopify.shopify_orders (
            id VARCHAR,
            name VARCHAR,
            email VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            total_price VARCHAR,
            financial_status VARCHAR,
            fulfillment_status VARCHAR
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS shopify.shopify_customers (
            id VARCHAR,
            first_name VARCHAR,
            last_name VARCHAR,
            email VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """
    )


def default_db_path() -> Path:
    """Project root data.duckdb (same convention as pipeline Airflow DAG)."""
    return Path(__file__).resolve().parent.parent / "data.duckdb"
