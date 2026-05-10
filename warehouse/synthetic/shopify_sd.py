"""Synthetic Shopify ``shopify.products`` via SDV (dummy package)."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _bootstrap_shopify_products_seed(con: duckdb.DuckDBPyConnection) -> None:
    """Ensure ``shopify.products`` exists with rows so SDV can fit."""
    from greenfield.schema import ensure_shopify_reconcile_stub_tables

    ensure_shopify_reconcile_stub_tables(con)
    try:
        n = con.execute("SELECT COUNT(*) FROM shopify.products").fetchone()[0]
        if n > 0:
            return
    except Exception:
        pass

    # Prefer copying from live-shaped ``shopify_products`` if present
    try:
        cnt = con.execute("SELECT COUNT(*) FROM shopify.shopify_products").fetchone()[0]
        if cnt and cnt > 0:
            con.execute(
                """
                CREATE TABLE shopify.products AS
                SELECT
                    cast(id as varchar) AS id,
                    title,
                    body_html,
                    vendor,
                    product_type,
                    handle,
                    template_suffix,
                    tags,
                    status,
                    created_at,
                    updated_at,
                    published_at,
                    options,
                    variants,
                    images,
                    featured_image
                FROM shopify.shopify_products
                LIMIT 100
                """
            )
            return
    except Exception:
        pass

    con.execute(
        """
        CREATE TABLE shopify.products (
            id VARCHAR,
            title VARCHAR,
            body_html VARCHAR,
            vendor VARCHAR,
            product_type VARCHAR,
            handle VARCHAR,
            template_suffix VARCHAR,
            tags VARCHAR,
            status VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            published_at TIMESTAMP,
            options JSON,
            variants JSON,
            images JSON,
            featured_image JSON
        )
        """
    )
    for i in range(25):
        con.execute(
            """
            INSERT INTO shopify.products VALUES (
                ?, ?, '', ?, 'supply', ?, '', '', 'ACTIVE',
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
                '[]'::JSON, '[]'::JSON, '[]'::JSON, NULL::JSON
            )
            """,
            [f"gid://shopify/Product/{i+1}", f"Seed product {i}", "GreenField", f"hdl-{i}"],
        )


def run_synthetic_shopify_products(db_path: Path | str, num_rows: int = 500) -> int:
    sys.path.append(str(REPO_ROOT / "dummy"))
    n0 = 0
    con = duckdb.connect(str(db_path))
    try:
        _bootstrap_shopify_products_seed(con)
        n0 = con.execute("SELECT COUNT(*) FROM shopify.products").fetchone()[0]
    finally:
        con.close()

    try:
        from synthetic_data_generator import generate_synthetic_data, save_synthetic_data_to_duckdb
    except ImportError:
        return int(n0)

    tables = ["shopify.products"]
    data = generate_synthetic_data(tables=tables, db_path=str(db_path), num_rows=num_rows)
    save_synthetic_data_to_duckdb(data, db_path=str(db_path), replace_existing=True)
    return num_rows
