"""
Post-QA: map Greenfield keys to Shopify GIDs and prepare Admin GraphQL exports.

This module records mappings in ``greenfield.shopify_id_mapping`` and provides
dry-run builders for product/order payloads. It does not call the live API unless
``execute_graphql`` is invoked with credentials present.
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

import duckdb

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data.duckdb"


def ensure_mapping_schema(con: duckdb.DuckDBPyConnection) -> None:
    from greenfield.schema import apply_greenfield_schema

    apply_greenfield_schema(con)


def record_mapping(
    con: duckdb.DuckDBPyConnection,
    entity_type: str,
    greenfield_key: str,
    *,
    shopify_gid: str | None = None,
    shopify_numeric_id: str | None = None,
    notes: str | None = None,
) -> str:
    """Insert a row into ``greenfield.shopify_id_mapping``."""
    mid = str(uuid.uuid4())
    con.execute(
        """
        INSERT INTO greenfield.shopify_id_mapping
        (mapping_id, entity_type, greenfield_key, shopify_gid, shopify_numeric_id, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [mid, entity_type, greenfield_key, shopify_gid, shopify_numeric_id, notes],
    )
    return mid


def shopify_gid(resource: str, numeric_id: str | int) -> str:
    """Build Admin GraphQL–style GID."""
    return f"gid://shopify/{resource}/{numeric_id}"


def export_product_mutations_dry_run(
    con: duckdb.DuckDBPyConnection,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Build ``productCreate``-style input dicts from ``greenfield.extracted_products``.

    Values are JSON-serializable for logging or bulk API calls later.
    """
    rows = con.execute(
        """
        SELECT extraction_id, doc_id, title, vendor, product_type, variants, tags
        FROM greenfield.extracted_products
        LIMIT ?
        """,
        [limit],
    ).fetchall()
    out: list[dict[str, Any]] = []
    for extraction_id, doc_id, title, vendor, product_type, variants, tags in rows:
        v = variants
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                v = []
        payload = {
            "mutation": "productCreate",
            "variables": {
                "input": {
                    "title": title,
                    "vendor": vendor,
                    "productType": product_type,
                    "tags": [t.strip() for t in tags.split(",") if t.strip()] if isinstance(tags, str) else (tags or []),
                    "variants": v if isinstance(v, list) else [],
                }
            },
            "greenfield": {"extraction_id": extraction_id, "doc_id": doc_id},
        }
        out.append(payload)
    return out


def execute_graphql(
    shop_name: str | None,
    access_token: str | None,
    query: str,
    variables: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute Admin GraphQL (optional). Uses ``SHOPIFY_SHOP_NAME`` and
    ``SHOPIFY_API_PASSWORD`` (access token) when args omitted.
    """
    import requests

    shop = shop_name or os.getenv("SHOPIFY_SHOP_NAME")
    token = access_token or os.getenv("SHOPIFY_API_PASSWORD") or os.getenv("SHOPIFY_ACCESS_TOKEN")
    if not shop or not token:
        raise RuntimeError("Missing SHOPIFY_SHOP_NAME or access token for GraphQL export.")

    version = os.getenv("SHOPIFY_API_VERSION", "2025-07")
    url = f"https://{shop}.myshopify.com/admin/api/{version}/graphql.json"
    r = requests.post(
        url,
        headers={"Content-Type": "application/json", "X-Shopify-Access-Token": token},
        json={"query": query, "variables": variables or {}},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def run_export_dry_run_cli(db_path: Path | None = None, limit: int = 10) -> None:
    """CLI helper: print JSON payloads to stdout."""
    p = Path(db_path or DEFAULT_DB)
    con = duckdb.connect(str(p))
    try:
        ensure_mapping_schema(con)
        payloads = export_product_mutations_dry_run(con, limit=limit)
        print(json.dumps(payloads, indent=2, default=str))
    finally:
        con.close()


if __name__ == "__main__":
    run_export_dry_run_cli()
