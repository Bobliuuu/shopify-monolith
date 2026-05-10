"""
Load non-Shopify / legacy flat files into ``legacy`` schema with YAML column mapping.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import yaml

from warehouse.stub_schemas import apply_stub_integration_schemas


def load_legacy_csv(
    con: duckdb.DuckDBPyConnection,
    csv_path: Path | str,
    mapping: dict[str, Any],
    *,
    ingestion_mode: str = "live",
) -> int:
    apply_stub_integration_schemas(con)
    p = Path(csv_path)
    if not p.is_file():
        raise FileNotFoundError(p)

    target = mapping.get("target_table", "orders_csv_stub")
    colmap: dict[str, str] = mapping.get("columns") or {}
    full = f"legacy.{target}"

    df = pd.read_csv(p)
    inserted = 0
    for _, row in df.iterrows():
        mapped: dict[str, Any] = {}
        for tgt, src in colmap.items():
            if src in df.columns:
                mapped[tgt] = row.get(src)
        raw = json.dumps(row.to_dict(), default=str)
        con.execute(
            f"""
            INSERT INTO {full}
            (external_order_id, customer_email, order_total, currency, placed_at, raw_row, ingestion_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                str(mapped.get("external_order_id") or "") or None,
                str(mapped.get("customer_email") or "") or None,
                float(mapped.get("order_total") or 0) if mapped.get("order_total") is not None else None,
                str(mapped.get("currency") or "CAD"),
                pd.to_datetime(mapped.get("placed_at"), errors="coerce"),
                raw,
                ingestion_mode,
            ],
        )
        inserted += 1
    return inserted


def load_mapping_file(path: Path | str) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
