from pathlib import Path

import duckdb

_STUB_SQL = Path(__file__).resolve().parent / "sql" / "stub_integrations.sql"


def apply_stub_integration_schemas(con: duckdb.DuckDBPyConnection) -> None:
    """Create ga4, google_ads, customerio, legacy stub tables."""
    con.execute(_STUB_SQL.read_text(encoding="utf-8"))
