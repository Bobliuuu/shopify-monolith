"""Shared path to monolith DuckDB (repo root ``data.duckdb``)."""

from pathlib import Path

DLT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = DLT_ROOT.parent
MONOLITH_DUCKDB = REPO_ROOT / "data.duckdb"
