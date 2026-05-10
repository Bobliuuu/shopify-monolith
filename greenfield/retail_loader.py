"""Load raw/retail/*.jsonl into greenfield.retail_* tables (ground truth layer)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

import duckdb

# Tables emitted by scripts/generator.py write_retail_exports
RETAIL_TABLE_FILES: tuple[str, ...] = (
    "customers",
    "products",
    "inventory_locations",
    "inventory_levels",
    "orders",
    "fulfillments",
    "refunds",
    "returns",
    "shipping_events",
    "payment_transactions",
    "tax_lines",
    "discounts",
    "shopify_payouts",
    "supplier_purchase_orders",
    "receiving_events",
    "inventory_adjustments",
)


def load_retail_jsonl(
    con: duckdb.DuckDBPyConnection,
    retail_dir: Path | str,
    *,
    replace: bool = True,
    tables: Iterable[str] | None = None,
) -> dict[str, int]:
    """
    Load each ``{table}.jsonl`` into ``greenfield.retail_{table}``.

    Returns mapping table_name -> row count.
    """
    root = Path(retail_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"Retail directory not found: {root}")

    want = set(tables) if tables else None
    counts: dict[str, int] = {}

    for name in RETAIL_TABLE_FILES:
        if want is not None and name not in want:
            continue
        path = root / f"{name}.jsonl"
        if not path.is_file():
            continue
        tgt = f"retail_{name}"
        qualified = f"greenfield.{tgt}"
        if replace:
            con.execute(f"DROP TABLE IF EXISTS {qualified}")
            con.execute(
                f"""
                CREATE TABLE {qualified} AS
                SELECT * FROM read_json_auto(?, filename=true, maximum_depth=8)
                """,
                [str(path)],
            )
        else:
            con.execute(
                f"""
                INSERT INTO {qualified}
                SELECT * FROM read_json_auto(?, filename=true, maximum_depth=8)
                """,
                [str(path)],
            )
        n = con.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0]
        counts[name] = int(n)

    return counts


def retail_load_id(retail_dir: Path | str) -> str:
    """Stable id from paths + content hashes (for batch bookkeeping)."""
    root = Path(retail_dir)
    h = hashlib.sha256()
    for name in RETAIL_TABLE_FILES:
        p = root / f"{name}.jsonl"
        if p.is_file():
            h.update(name.encode())
            h.update(p.read_bytes())
    return h.hexdigest()[:24]
