#!/usr/bin/env python3
"""Generate real-economy-aware insights and action queue from DuckDB."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data.duckdb"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_tables(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS analytics.daily_action_queue (
            action_id VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            severity VARCHAR,
            action_type VARCHAR,
            message VARCHAR,
            expected_impact VARCHAR,
            payload JSON
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS analytics.executive_digest (
            digest_id VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            summary JSON
        )
        """
    )


def build_insights(con: duckdb.DuckDBPyConnection) -> dict:
    order_metrics = con.execute(
        """
        SELECT
            COUNT(*) AS orders,
            SUM(COALESCE(grand_total, 0)) AS revenue,
            AVG(COALESCE(grand_total, 0)) AS aov
        FROM greenfield.extracted_orders
        """
    ).fetchone()
    sku_risk = con.execute(
        """
        SELECT sku, SUM(COALESCE(qty, 0)) AS sold_qty
        FROM greenfield.extracted_line_items
        GROUP BY sku
        ORDER BY sold_qty DESC
        LIMIT 10
        """
    ).fetchall()
    return {
        "orders": int(order_metrics[0] or 0),
        "revenue": float(order_metrics[1] or 0.0),
        "aov": float(order_metrics[2] or 0.0),
        "top_demand_skus": [{"sku": r[0], "sold_qty": float(r[1] or 0)} for r in sku_risk],
    }


def write_actions(con: duckdb.DuckDBPyConnection, insights: dict) -> int:
    actions: list[tuple[str, str, str, str, str, str]] = []
    if insights["aov"] < 150:
        actions.append(
            (
                "act_aov_1",
                "high",
                "pricing",
                "Average order value is low; evaluate bundle/upsell pricing.",
                "Increase AOV 5-10%",
                json.dumps({"metric": "aov", "value": insights["aov"]}),
            )
        )
    if insights["top_demand_skus"]:
        actions.append(
            (
                "act_inv_1",
                "medium",
                "inventory",
                "Top SKU demand detected; review inventory and restock cadence.",
                "Reduce stockouts 10-20%",
                json.dumps({"top_skus": insights["top_demand_skus"][:3]}),
            )
        )
    for row in actions:
        con.execute(
            """
            INSERT INTO analytics.daily_action_queue
            (action_id, severity, action_type, message, expected_impact, payload)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            row,
        )
    return len(actions)


def write_digest(con: duckdb.DuckDBPyConnection, insights: dict) -> str:
    digest_id = f"digest_{int(datetime.now(timezone.utc).timestamp())}"
    con.execute(
        """
        INSERT INTO analytics.executive_digest (digest_id, summary)
        VALUES (?, ?)
        """,
        [digest_id, json.dumps(insights)],
    )
    return digest_id


def run(db_path: Path) -> dict:
    con = duckdb.connect(str(db_path))
    try:
        ensure_tables(con)
        insights = build_insights(con)
        actions = write_actions(con, insights)
        digest_id = write_digest(con, insights)
        return {"insights": insights, "actions_created": actions, "digest_id": digest_id}
    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create insights + action queue + exec digest.")
    parser.add_argument("--db-path", default=str(DEFAULT_DB))
    parser.add_argument("--output", default="data/insights/latest_digest.json")
    args = parser.parse_args()
    result = run(Path(args.db_path))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"generated_at": _utc_now(), **result}, indent=2), encoding="utf-8")
    print(f"Insights written: {out}")


if __name__ == "__main__":
    main()
