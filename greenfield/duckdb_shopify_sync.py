#!/usr/bin/env python3
"""Near-real-time DuckDB -> Shopify catalog and price sync."""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from greenfield.shopify_export import execute_graphql
from greenfield.schema import apply_greenfield_schema

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data.duckdb"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_sync_schema(con: duckdb.DuckDBPyConnection) -> None:
    apply_greenfield_schema(con)
    con.execute("CREATE SCHEMA IF NOT EXISTS greenfield")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS greenfield.shopify_sync_cursor (
            cursor_id VARCHAR PRIMARY KEY,
            last_ts TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS greenfield.shopify_sync_events (
            event_id VARCHAR,
            extraction_id VARCHAR,
            product_title VARCHAR,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR,
            reason VARCHAR,
            details JSON
        )
        """
    )
    con.execute(
        """
        INSERT INTO greenfield.shopify_sync_cursor (cursor_id, last_ts)
        SELECT 'catalog', TIMESTAMP '1970-01-01 00:00:00'
        WHERE NOT EXISTS (SELECT 1 FROM greenfield.shopify_sync_cursor WHERE cursor_id = 'catalog')
        """
    )


@dataclass
class Guardrails:
    min_price: float
    max_price: float
    max_change_ratio: float


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_variants(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = []
    if not isinstance(raw, list):
        return []
    variants: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        price = _to_float(item.get("price"), default=0.0)
        variants.append(
            {
                "sku": str(item.get("sku") or ""),
                "price": price,
                "inventoryQuantity": int(_to_float(item.get("inventory_quantity"), default=0)),
            }
        )
    return variants


def _validate_price_guardrail(price: float, previous: float | None, rules: Guardrails) -> tuple[bool, str]:
    if price < rules.min_price or price > rules.max_price:
        return False, f"price_out_of_bounds:{price}"
    if previous is not None and previous > 0:
        ratio = abs(price - previous) / previous
        if ratio > rules.max_change_ratio:
            return False, f"price_delta_too_high:{ratio:.3f}"
    return True, "ok"


def _write_event(
    con: duckdb.DuckDBPyConnection,
    extraction_id: str,
    title: str,
    status: str,
    reason: str,
    details: dict[str, Any] | None = None,
) -> None:
    con.execute(
        """
        INSERT INTO greenfield.shopify_sync_events
        (event_id, extraction_id, product_title, status, reason, details)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            f"evt_{int(time.time() * 1000)}_{extraction_id}",
            extraction_id,
            title,
            status,
            reason,
            json.dumps(details or {}),
        ],
    )


def _sync_product(shop_name: str, token: str, product: dict[str, Any]) -> dict[str, Any]:
    mutation = """
    mutation productSet($identifier: ProductSetIdentifiers, $input: ProductSetInput!) {
      productSet(identifier: $identifier, input: $input, synchronous: true) {
        product { id title handle }
        userErrors { field message }
      }
    }
    """
    variables = {
        "identifier": {"handle": product["handle"]},
        "input": {
            "title": product["title"],
            "handle": product["handle"],
            "productType": product["productType"],
            "vendor": product["vendor"],
            "status": "ACTIVE" if product["status"] == "active" else "DRAFT",
            "tags": product["tags"],
            "variants": [
                {
                    "sku": v["sku"],
                    "price": f"{v['price']:.2f}",
                    "inventoryQuantities": [],
                }
                for v in product["variants"]
            ],
        },
    }
    return execute_graphql(shop_name, token, mutation, variables)


def run_once(db_path: Path, guardrails: Guardrails) -> dict[str, Any]:
    shop_name = os.getenv("SHOPIFY_SHOP_NAME")
    token = os.getenv("SHOPIFY_API_PASSWORD") or os.getenv("SHOPIFY_ACCESS_TOKEN")
    if not shop_name or not token:
        raise RuntimeError("Missing SHOPIFY_SHOP_NAME and access token.")

    con = duckdb.connect(str(db_path))
    try:
        ensure_sync_schema(con)
        last_ts = con.execute(
            "SELECT last_ts FROM greenfield.shopify_sync_cursor WHERE cursor_id='catalog'"
        ).fetchone()[0]
        rows = con.execute(
            """
            SELECT extraction_id, title, vendor, product_type, handle, status, variants, tags, _ingested_at
            FROM greenfield.extracted_products
            WHERE COALESCE(updated_at, _ingested_at) > ?
            ORDER BY COALESCE(updated_at, _ingested_at) ASC
            """,
            [last_ts],
        ).fetchall()

        synced = 0
        skipped = 0
        newest_ts = last_ts
        for extraction_id, title, vendor, product_type, handle, status, variants, tags, row_ts in rows:
            parsed_variants = _extract_variants(variants)
            if not parsed_variants:
                skipped += 1
                _write_event(con, extraction_id, title or "", "skipped", "no_variants")
                newest_ts = row_ts
                continue
            guardrail_failed = False
            previous_price = None
            for variant in parsed_variants:
                ok, reason = _validate_price_guardrail(variant["price"], previous_price, guardrails)
                if not ok:
                    guardrail_failed = True
                    _write_event(
                        con,
                        extraction_id,
                        title or "",
                        "blocked",
                        reason,
                        {"variant": variant},
                    )
                previous_price = variant["price"]
            if guardrail_failed:
                skipped += 1
                newest_ts = row_ts
                continue

            payload = {
                "title": title or "Untitled Product",
                "vendor": vendor or "",
                "productType": product_type or "",
                "handle": handle or f"product-{extraction_id[-8:]}",
                "status": (status or "draft").lower(),
                "tags": [t.strip() for t in (tags or "").split(",") if t.strip()],
                "variants": parsed_variants,
            }
            try:
                response = _sync_product(shop_name, token, payload)
                errors = (
                    response.get("data", {})
                    .get("productSet", {})
                    .get("userErrors", [])
                )
                if errors:
                    _write_event(
                        con,
                        extraction_id,
                        title or "",
                        "failed",
                        "graphql_user_errors",
                        {"errors": errors},
                    )
                    skipped += 1
                else:
                    _write_event(con, extraction_id, title or "", "synced", "ok")
                    synced += 1
            except Exception as exc:  # noqa: BLE001
                _write_event(
                    con,
                    extraction_id,
                    title or "",
                    "failed",
                    "exception",
                    {"error": str(exc)},
                )
                skipped += 1
            newest_ts = row_ts

        con.execute(
            """
            UPDATE greenfield.shopify_sync_cursor
            SET last_ts = ?, updated_at = CURRENT_TIMESTAMP
            WHERE cursor_id = 'catalog'
            """,
            [newest_ts],
        )
        return {"synced": synced, "skipped": skipped, "from": str(last_ts), "to": str(newest_ts)}
    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync DuckDB extracted products into Shopify.")
    parser.add_argument("--db-path", default=str(DEFAULT_DB))
    parser.add_argument("--min-price", type=float, default=0.01)
    parser.add_argument("--max-price", type=float, default=50000.0)
    parser.add_argument("--max-change-ratio", type=float, default=0.75)
    args = parser.parse_args()
    report = run_once(
        Path(args.db_path),
        Guardrails(
            min_price=args.min_price,
            max_price=args.max_price,
            max_change_ratio=args.max_change_ratio,
        ),
    )
    print(json.dumps({"generated_at": _utc_now(), **report}, indent=2))


if __name__ == "__main__":
    main()
