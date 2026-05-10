"""
Orchestrate nightly warehouse loads: metadata, Shopify, Stripe, stub analytics, optional Greenfield, dbt.

Designed for Airflow ``commerce_warehouse_nightly`` and local CLI.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DLT_ROOT = REPO_ROOT / "dlt"

from warehouse.metadata import (
    apply_meta_schema,
    complete_ingestion_run,
    complete_warehouse_run,
    default_data_db_path,
    start_ingestion_run,
    start_warehouse_run,
)
from warehouse.stub_schemas import apply_stub_integration_schemas
from warehouse.synthetic.stub_seeds import seed_stub_tables, seed_synthetic_stripe
from warehouse.synthetic.shopify_sd import run_synthetic_shopify_products


def _ensure_paths() -> None:
    for p in (REPO_ROOT, DLT_ROOT):
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)


def run_nightly(
    conf: dict[str, Any] | None = None,
    *,
    git_sha: str | None = None,
    airflow_dag_id: str | None = None,
    airflow_run_id: str | None = None,
    run_dbt: bool = True,
    dbt_select: str = "+tag:core +tag:mart tag:analytics_view",
) -> dict[str, Any]:
    """
    Execute full nightly batch. ``conf`` keys:

    - ``shopify_data_mode``: ``live`` | ``synthetic``
    - ``stripe_data_mode``: ``live`` | ``synthetic``
    - ``allow_synthetic_fallback``: if Shopify live fails, fall back to SDV
    - ``stub_integrations``: seed GA4 / Ads / Customer.io synthetic tables (default True)
    - ``greenfield_dataset_root``: optional path string for corpus ingestion
    - ``greenfield_max_docs``: optional cap for greenfield batch
    - ``run_dbt``, ``dbt_select``: override kwargs defaults when present in ``conf``
      (default builds core facts/dims and their upstream, greenfield marts and upstream, and BI ``analytics_view`` models).
    """
    _ensure_paths()
    conf = dict(conf or {})
    run_dbt_flag = bool(conf.get("run_dbt", run_dbt))
    dbt_sel = str(conf.get("dbt_select", dbt_select))
    db_path = default_data_db_path()

    import duckdb

    wr = None
    con = duckdb.connect(str(db_path))
    apply_meta_schema(con)
    apply_stub_integration_schemas(con)

    wr = start_warehouse_run(
        con,
        params=conf,
        git_sha=git_sha or os.getenv("GIT_SHA"),
        dag_id=airflow_dag_id,
        airflow_run_id=airflow_run_id,
    )
    result: dict[str, Any] = {"warehouse_run_id": wr, "steps": []}

    try:
        # --- Shopify ---
        smode = conf.get("shopify_data_mode", "live")
        if smode == "live":
            from pipelines.run_shopify_pipeline import run as run_shopify_try

            ok = run_shopify_try(record_metadata=True, warehouse_run_id=wr)

            if not ok and conf.get("allow_synthetic_fallback", True):
                iid = start_ingestion_run(con, wr, "shopify", "synthetic")
                n = run_synthetic_shopify_products(db_path)
                complete_ingestion_run(con, iid, rows_affected=n, detail={"fallback": True})
                result["steps"].append({"shopify": "synthetic_fallback", "rows": n})
            elif not ok:
                raise RuntimeError("Shopify DLT pipeline failed (set allow_synthetic_fallback or use shopify_data_mode=synthetic)")
            else:
                result["steps"].append({"shopify": "live", "ok": ok})
        else:
            iid = start_ingestion_run(con, wr, "shopify", "synthetic")
            n = run_synthetic_shopify_products(db_path)
            complete_ingestion_run(con, iid, rows_affected=n)
            result["steps"].append({"shopify": "synthetic", "rows": n})

        # --- Stripe ---
        want_stripe_live = conf.get("stripe_data_mode", "live") == "live"
        has_stripe_key = bool(os.getenv("STRIPE_API_KEY"))
        if want_stripe_live and has_stripe_key:
            from pipelines.run_stripe_pipeline import run as run_stripe

            ok = run_stripe(record_metadata=True, warehouse_run_id=wr)
            result["steps"].append({"stripe": "live", "ok": ok})
        elif want_stripe_live and not has_stripe_key:
            if conf.get("allow_synthetic_fallback", True):
                iid = start_ingestion_run(con, wr, "stripe", "synthetic")
                n = seed_synthetic_stripe(con)
                complete_ingestion_run(con, iid, rows_affected=n)
                result["steps"].append({"stripe": "synthetic", "rows": n, "reason": "missing_STRIPE_API_KEY"})
            else:
                raise RuntimeError("stripe_data_mode=live but STRIPE_API_KEY is not set")
        else:
            iid = start_ingestion_run(con, wr, "stripe", "synthetic")
            n = seed_synthetic_stripe(con)
            complete_ingestion_run(con, iid, rows_affected=n)
            result["steps"].append({"stripe": "synthetic", "rows": n})

        # --- Marketing analytics stubs (GA4, Google Ads, Customer.io) ---
        if conf.get("stub_integrations", True):
            iid = start_ingestion_run(con, wr, "marketing_analytics", "synthetic")
            counts = seed_stub_tables(con)
            complete_ingestion_run(
                con,
                iid,
                rows_affected=sum(counts.values()),
                detail=counts,
            )
            result["steps"].append({"marketing_stubs": counts})

        # --- Optional Greenfield corpus ---
        mx = conf.get("greenfield_max_docs")
        if mx is not None and int(mx) < 0:
            mx = None
        gf_root = (conf.get("greenfield_dataset_root") or "").strip() or None
        if gf_root:
            from greenfield.pipeline import run_ingestion_batch

            iid = start_ingestion_run(con, wr, "greenfield", "live")
            try:
                gf_result = run_ingestion_batch(
                    gf_root,
                    db_path,
                    max_docs=mx,
                    load_retail=conf.get("greenfield_load_retail", True),
                    replace_retail=conf.get("greenfield_replace_retail", True),
                )
                complete_ingestion_run(
                    con,
                    iid,
                    rows_affected=gf_result.get("documents_processed"),
                    detail=gf_result,
                )
                result["steps"].append({"greenfield": gf_result})
            except Exception as e:
                complete_ingestion_run(con, iid, status="failed", error_message=str(e))
                raise

        complete_warehouse_run(con, wr, status="completed")
        result["status"] = "completed"

        con.close()
        con = None

        if run_dbt_flag:
            env = os.environ.copy()
            env["DBT_DUCKDB_PATH"] = str(db_path.resolve())
            proc = subprocess.run(
                ["dbt", "run", "--select", dbt_sel],
                cwd=str(REPO_ROOT / "data"),
                env=env,
                capture_output=True,
                text=True,
            )
            result["dbt"] = {
                "returncode": proc.returncode,
                "stdout": proc.stdout[-8000:] if proc.stdout else "",
                "stderr": proc.stderr[-4000:] if proc.stderr else "",
            }
            if proc.returncode != 0:
                result["status"] = "completed_with_dbt_errors"

        return result
    except Exception as e:
        if con is not None and wr is not None:
            try:
                complete_warehouse_run(con, wr, status="failed", notes=str(e))
            except Exception:
                pass
        result["status"] = "failed"
        result["error"] = str(e)
        raise
    finally:
        if con is not None:
            con.close()


def main() -> None:
    conf_path = os.getenv("NIGHTLY_CONF_JSON")
    conf = json.loads(conf_path) if conf_path else {}
    out = run_nightly(conf)
    print(json.dumps(out, default=str, indent=2))


if __name__ == "__main__":
    main()
