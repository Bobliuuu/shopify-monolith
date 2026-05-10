"""DuckDB metadata schema: warehouse_run + ingestion_run lineage."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

_META_SQL = Path(__file__).resolve().parent / "sql" / "meta_schema.sql"


def default_data_db_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data.duckdb"


def apply_meta_schema(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(_META_SQL.read_text(encoding="utf-8"))


def start_warehouse_run(
    con: duckdb.DuckDBPyConnection,
    *,
    params: dict[str, Any] | None = None,
    git_sha: str | None = None,
    dag_id: str | None = None,
    airflow_run_id: str | None = None,
) -> str:
    apply_meta_schema(con)
    rid = f"wr_{uuid.uuid4().hex[:16]}"
    con.execute(
        """
        INSERT INTO meta.warehouse_run
        (run_id, started_at, status, git_sha, airflow_dag_id, airflow_run_id, params_json)
        VALUES (?, CURRENT_TIMESTAMP, 'running', ?, ?, ?, ?)
        """,
        [
            rid,
            git_sha,
            dag_id,
            airflow_run_id,
            json.dumps(params or {}),
        ],
    )
    return rid


def complete_warehouse_run(
    con: duckdb.DuckDBPyConnection,
    run_id: str,
    *,
    status: str = "completed",
    notes: str | None = None,
) -> None:
    con.execute(
        """
        UPDATE meta.warehouse_run
        SET completed_at = CURRENT_TIMESTAMP, status = ?, notes = COALESCE(?, notes)
        WHERE run_id = ?
        """,
        [status, notes, run_id],
    )


def start_ingestion_run(
    con: duckdb.DuckDBPyConnection,
    warehouse_run_id: str,
    integration: str,
    ingestion_mode: str,
) -> str:
    apply_meta_schema(con)
    iid = f"ir_{uuid.uuid4().hex[:16]}"
    con.execute(
        """
        INSERT INTO meta.ingestion_run
        (ingestion_id, warehouse_run_id, integration, ingestion_mode, started_at, status)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 'running')
        """,
        [iid, warehouse_run_id, integration, ingestion_mode],
    )
    return iid


def complete_ingestion_run(
    con: duckdb.DuckDBPyConnection,
    ingestion_id: str,
    *,
    rows_affected: int | None = None,
    status: str = "completed",
    error_message: str | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    con.execute(
        """
        UPDATE meta.ingestion_run
        SET completed_at = CURRENT_TIMESTAMP,
            status = ?,
            rows_affected = ?,
            error_message = ?,
            detail_json = ?
        WHERE ingestion_id = ?
        """,
        [
            status,
            rows_affected,
            error_message,
            json.dumps(detail) if detail else None,
            ingestion_id,
        ],
    )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
