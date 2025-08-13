from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s

# --- Paths --------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
PIPELINE_ROOT = HERE.parent  # ../
DATA_ROOT = PIPELINE_ROOT.parent  # ../../
DLT_ROOT = HERE.parent.parent / "dlt"  # ../../dlt

# Add project dirs to PYTHONPATH so imports work when Airflow parses the DAG
for p in (PIPELINE_ROOT, DLT_ROOT):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.append(p_str)

# --- Config -------------------------------------------------------------------
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Execution mode flags
DEBUG_MODE = True      # True -> generate dummy data with SDV; False -> run DLT pipeline
K8_MODE = True       # True -> run in Kubernetes pod; False -> run locally

# --- Callables ----------------------------------------------------------------
def generate_dummy_data():
    """Generate dummy Shopify product data using SDV."""
    from synthetic_data_generator import generate_synthetic_data, save_synthetic_data_to_duckdb

    tables = ["shopify.products"]
    db_path = str(DATA_ROOT / "data.duckdb")

    synthetic_data = generate_synthetic_data(
        tables=tables,
        db_path=db_path,
        num_rows=1000,
    )

    save_synthetic_data_to_duckdb(
        synthetic_data=synthetic_data,
        db_path=db_path,
        replace_existing=True,
    )
    print("✅ Generated and saved synthetic Shopify products data")

def run_dlt_pipeline():
    """Run the DLT Shopify pipeline."""
    from pipelines.run_shopify_pipeline import run
    run()

# --- DAG ----------------------------------------------------------------------
with DAG(
    dag_id="shopify_products_dag",
    description="Shopify products pipeline (debug uses SDV; prod runs DLT; k8 runs in Kubernetes)",
    default_args=default_args,
    schedule=timedelta(days=1),
    catchup=False,
    tags=["shopify", "dlt", "sdv", "kubernetes"],
) as dag:

    start = EmptyOperator(task_id="start")

    if K8_MODE:
        # Kubernetes mode: Run specific Python files in isolated pods
        if DEBUG_MODE:
            # K8 + Debug: Generate dummy data using synthetic_data_generator_k8.py
            generate_data_k8 = KubernetesPodOperator(
                task_id="generate_dummy_data_k8",
                namespace="default",
                image="python:3.11-slim",
                cmds=["bash", "-c"],
                arguments=[
                    """
                    pip install -r /opt/airflow/dags/../requirements.txt &&
                    python /opt/airflow/dags/synthetic_data_generator_k8.py
                    """
                ],
                volumes=[
                    k8s.V1Volume(
                        name="dags-volume",
                        persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
                            claim_name="airflow-dags-pvc"
                        )
                    )
                ],
                volume_mounts=[
                    k8s.V1VolumeMount(
                        name="dags-volume",
                        mount_path="/opt/airflow/dags"
                    )
                ],
                get_logs=True,
                is_delete_operator_pod=True,
            )
            start >> generate_data_k8
        else:
            # K8 + Production: Run DLT pipeline using run_shopify_pipeline.py
            run_pipeline_k8 = KubernetesPodOperator(
                task_id="run_dlt_pipeline_k8",
                namespace="default",
                image="python:3.11-slim",
                cmds=["bash", "-c"],
                arguments=[
                    """
                    pip install -r /opt/airflow/dags/../requirements.txt &&
                    python /opt/airflow/dags/run_shopify_pipeline.py
                    """
                ],
                volumes=[
                    k8s.V1Volume(
                        name="dags-volume",
                        persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
                            claim_name="airflow-dags-pvc"
                        )
                    )
                ],
                volume_mounts=[
                    k8s.V1VolumeMount(
                        name="dags-volume",
                        mount_path="/opt/airflow/dags"
                    )
                ],
                get_logs=True,
                is_delete_operator_pod=True,
            )
            start >> run_pipeline_k8

    else:
        # Local mode: Run in Airflow worker
        if DEBUG_MODE:
            generate_data = PythonOperator(
                task_id="generate_dummy_data",
                python_callable=generate_dummy_data,
            )
            start >> generate_data
        else:
            run_pipeline = PythonOperator(
                task_id="run_dlt_pipeline",
                python_callable=run_dlt_pipeline,
            )
            start >> run_pipeline
