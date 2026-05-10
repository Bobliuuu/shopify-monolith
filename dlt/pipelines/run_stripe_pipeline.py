#!/usr/bin/env python3
"""Stripe DLT pipeline into monolith ``data.duckdb`` (schema ``stripe``)."""

import os
import sys
from pathlib import Path

import dlt
from dotenv import load_dotenv

from pipelines._duckdb_path import MONOLITH_DUCKDB, REPO_ROOT

dlt_root = Path(__file__).resolve().parent.parent
sys.path.append(str(dlt_root))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def run(record_metadata: bool = False, warehouse_run_id: str | None = None) -> bool:
    ingestion_id = None
    con = None
    try:
        load_dotenv()
        if not os.getenv("STRIPE_API_KEY"):
            print("❌ STRIPE_API_KEY is not set")
            return False

        if record_metadata:
            import duckdb
            from warehouse.metadata import apply_meta_schema, start_ingestion_run

            con = duckdb.connect(str(MONOLITH_DUCKDB))
            apply_meta_schema(con)
            if not warehouse_run_id:
                raise ValueError("warehouse_run_id required when record_metadata=True")
            ingestion_id = start_ingestion_run(con, warehouse_run_id, "stripe", "live")

        from sources.stripe_source import stripe_source

        pipeline = dlt.pipeline(
            pipeline_name="stripe_pipeline",
            destination=dlt.destinations.duckdb(str(MONOLITH_DUCKDB)),
            dataset_name="stripe",
        )
        load_info = pipeline.run(stripe_source())
        print("✅ Stripe pipeline finished!")
        print(load_info)

        if con is not None and ingestion_id:
            from warehouse.metadata import complete_ingestion_run

            rows = 0
            for tbl in ("stripe_customers", "stripe_charges", "stripe_invoices"):
                try:
                    rows += con.execute(f"SELECT COUNT(*) FROM stripe.{tbl}").fetchone()[0]
                except Exception:
                    pass
            complete_ingestion_run(con, ingestion_id, rows_affected=int(rows), status="completed")

        return True
    except Exception as e:
        print(f"❌ Stripe pipeline failed: {e}")
        import traceback

        traceback.print_exc()
        if con is not None and ingestion_id:
            from warehouse.metadata import complete_ingestion_run

            complete_ingestion_run(con, ingestion_id, status="failed", error_message=str(e))
        return False
    finally:
        if con is not None:
            con.close()


def main():
    if not run():
        sys.exit(1)


if __name__ == "__main__":
    main()
