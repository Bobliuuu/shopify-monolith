"""
Nightly unified warehouse DAG: Shopify + Stripe + stub analytics + optional Greenfield + dbt core.

Conf (JSON) overrides defaults via Trigger DAG with configuration:

- ``shopify_data_mode``: ``live`` | ``synthetic``
- ``stripe_data_mode``: ``live`` | ``synthetic``
- ``allow_synthetic_fallback``: bool (default True)
- ``stub_integrations``: bool (default True)
- ``greenfield_dataset_root``: optional path string
- ``greenfield_max_docs``: optional int
- ``run_dbt``: bool (default True)
"""

from __future__ import annotations

import json
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
    "retries": 0,
    "retry_delay": timedelta(minutes=10),
}


def _run_commerce_nightly(**context):
    from warehouse.nightly_runner import run_nightly

    dag_run = context.get("dag_run")
    conf = dict(context.get("params") or {})
    if dag_run and dag_run.conf:
        conf.update(dag_run.conf)

    return run_nightly(
        conf,
        airflow_dag_id=context.get("dag").dag_id if context.get("dag") else None,
        airflow_run_id=str(context.get("run_id") or ""),
    )


with DAG(
    dag_id="commerce_warehouse_nightly",
    description="Unified nightly load: meta lineage + Shopify/Stripe + stubs + optional Greenfield + dbt core",
    default_args=default_args,
    schedule="@daily",
    catchup=False,
    tags=["warehouse", "shopify", "stripe", "analytics", "dbt"],
    params={
        "shopify_data_mode": Param("live", type="string"),
        "stripe_data_mode": Param("live", type="string"),
        "allow_synthetic_fallback": Param(True, type="boolean"),
        "stub_integrations": Param(True, type="boolean"),
        "greenfield_dataset_root": Param("", type="string"),
        "greenfield_max_docs": Param(-1, type="integer"),
        "run_dbt": Param(True, type="boolean"),
        "dbt_select": Param("+tag:core +tag:mart tag:analytics_view", type="string"),
    },
) as dag:
    start = EmptyOperator(task_id="start")
    run_batch = PythonOperator(
        task_id="run_commerce_warehouse_batch",
        python_callable=_run_commerce_nightly,
    )
    end = EmptyOperator(task_id="end")
    start >> run_batch >> end
