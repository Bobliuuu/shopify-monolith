"""
Greenfield OCR → cleaning → DuckDB ingestion DAG.

Mirrors path conventions from ``shopify_products_dag``: repo-root ``data.duckdb``,
Python path includes project root so ``greenfield`` imports resolve.

Environment (optional):
  GREENFIELD_DATASET_ROOT — absolute path to dataset root (contains manifests/, raw/, …).
  GREENFIELD_DUCKDB_PATH — DuckDB file path (default: repo ``data.duckdb``).
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.models.param import Param
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

HERE = Path(__file__).resolve().parent
PIPELINE_ROOT = HERE.parent
DATA_ROOT = PIPELINE_ROOT.parent

for p in (DATA_ROOT,):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def _resolve_dataset_root(conf: dict, params: dict) -> Path:
    """Local dataset root. For R2-hosted assets, sync to disk first and point env here."""
    for key in ("dataset_root", "greenfield_dataset_root"):
        v = conf.get(key) or params.get(key)
        if v and str(v).strip():
            return Path(str(v)).resolve()
    env = os.getenv("GREENFIELD_DATASET_ROOT")
    if env:
        return Path(env).resolve()
    return (DATA_ROOT / "tmp_greenfield_test").resolve()


def _resolve_db_path(conf: dict, params: dict) -> Path:
    v = conf.get("duckdb_path") or params.get("duckdb_path")
    if v and str(v).strip():
        return Path(str(v)).resolve()
    v = os.getenv("GREENFIELD_DUCKDB_PATH")
    if v:
        return Path(str(v)).resolve()
    return (DATA_ROOT / "data.duckdb").resolve()


def run_greenfield_ingestion(**context):
    from greenfield.pipeline import run_ingestion_batch

    dag_run = context.get("dag_run")
    conf = (dag_run.conf if dag_run else {}) or {}
    params = context.get("params") or {}

    dataset_root = _resolve_dataset_root(conf, params)
    db_path = _resolve_db_path(conf, params)
    eval_mode = conf.get("eval_mode", params.get("eval_mode", "ground_truth"))
    split = conf.get("split", params.get("split")) or ""
    max_docs = conf.get("max_docs")
    if max_docs is None:
        max_docs = params.get("max_docs", -1)
    batch_id = conf.get("batch_id", params.get("batch_id")) or None
    if batch_id is not None and str(batch_id).strip() == "":
        batch_id = None
    load_retail = conf.get("load_retail", params.get("load_retail", True))
    replace_retail = conf.get("replace_retail", params.get("replace_retail", True))

    split_filter = split.strip() or None
    if max_docs is not None:
        max_docs = int(max_docs)
        if max_docs < 0:
            max_docs = None

    if not dataset_root.is_dir():
        raise FileNotFoundError(
            f"GREENFIELD_DATASET_ROOT / dataset_root must be a local directory (sync R2 here first): {dataset_root}"
        )

    result = run_ingestion_batch(
        dataset_root,
        db_path,
        batch_id=batch_id,
        eval_mode=eval_mode,
        split=split_filter,
        load_retail=bool(load_retail),
        replace_retail=bool(replace_retail),
        max_docs=max_docs,
    )
    print(f"Greenfield ingestion result: {result}")
    return result


with DAG(
    dag_id="greenfield_ingestion_dag",
    description="Greenfield manifest → OCR/clean → extract → DuckDB (greenfield schema)",
    default_args=default_args,
    schedule=timedelta(days=1),
    catchup=False,
    tags=["greenfield", "ocr", "duckdb"],
    params={
        "eval_mode": Param("ground_truth", type="string", description="ground_truth | noisy | raw_artifact | image_ocr"),
        "split": Param("", type="string", description="train | val | test (leave empty for all)"),
        "max_docs": Param(-1, type="integer", description="-1 = no cap"),
        "batch_id": Param("", type="string", description="Optional stable batch id"),
        "dataset_root": Param("", type="string", description="Override path (else GREENFIELD_DATASET_ROOT or tmp_greenfield_test)"),
        "duckdb_path": Param("", type="string", description="Override DuckDB path (else GREENFIELD_DUCKDB_PATH or data.duckdb)"),
        "load_retail": Param(True, type="boolean"),
        "replace_retail": Param(True, type="boolean"),
    },
) as dag:
    start = EmptyOperator(task_id="start")
    ingest = PythonOperator(
        task_id="run_greenfield_ingestion",
        python_callable=run_greenfield_ingestion,
    )
    end = EmptyOperator(task_id="end")
    start >> ingest >> end
