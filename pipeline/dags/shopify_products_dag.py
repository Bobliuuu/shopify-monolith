from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from airflow.models.param import Param

# --- Paths --------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
PIPELINE_ROOT = HERE.parent  # ../
DATA_ROOT = PIPELINE_ROOT.parent  # ../../
DLT_ROOT = HERE.parent.parent / "dlt"  # ../../dlt
DUMMY_ROOT = HERE.parent.parent / "dummy"  # ../../dummy

# Add project dirs to PYTHONPATH so imports work when Airflow parses the DAG
for p in (PIPELINE_ROOT, DLT_ROOT, DUMMY_ROOT):
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

def _as_bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "t", "yes", "y", "on")
    return bool(v)

# --- Callables ----------------------------------------------------------------
def generate_dummy_data():
    """Generate dummy Shopify product data using SDV."""
    print("🚀 Starting generate_dummy_data task...")
    
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
    """Run the DLT Shopify pipeline using the importable package."""
    print("🚀 Starting run_dlt_pipeline task...")
    
    try:
        print("🚀 Starting Shopify DLT pipeline...")
        
        # Import from the DLT package
        from dlt.pipelines.run_shopify_pipeline import run
        
        print("📦 DLT pipeline imported successfully")
        
        # Run the pipeline
        success = run()
        
        if success:
            print("✅ DLT pipeline completed successfully!")
        else:
            raise Exception("Pipeline returned False")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"Python path: {sys.path}")
        print(f"DLT_ROOT: {DLT_ROOT}")
        raise
    except Exception as e:
        print(f"❌ Error running DLT pipeline: {e}")
        raise

def decide_execution_path(**context):
    """Decide which execution path to take based on DAG parameters."""
    dag_run = context.get("dag_run")
    conf = (dag_run.conf if dag_run else {}) or {}
    params = context.get("params", {})
    
    debug_mode = _as_bool(conf.get("debug_mode", params.get("debug_mode")))
    k8_mode = _as_bool(conf.get("k8_mode", params.get("k8_mode")))
    
    print(f"🔍 Decision inputs -> conf={conf} params={params}")
    print(f"🔍 Resolved: debug_mode={debug_mode}, k8_mode={k8_mode}")
    
    if k8_mode:
        if debug_mode:
            return "generate_dummy_data_k8"
        else:
            return "run_dlt_pipeline_k8"
    else:
        if debug_mode:
            return "generate_dummy_data"
        else:
            return "run_dlt_pipeline"

# --- DAG ----------------------------------------------------------------------
with DAG(
    dag_id="shopify_products_dag",
    description="Shopify products pipeline (debug uses SDV; prod runs DLT; k8 runs in Kubernetes)",
    default_args=default_args,
    schedule=timedelta(days=1),
    catchup=False,
    tags=["shopify", "dlt", "sdv", "kubernetes"],
    # Configuration parameters with defaults
    params = {
        "debug_mode": Param(False, type="boolean"),
        "k8_mode": Param(False, type="boolean"),
    }
) as dag:

    start = EmptyOperator(task_id="start")
    
    # Decision task that evaluates parameters at runtime
    decision = BranchPythonOperator(
        task_id="decide_execution_path",
        python_callable=decide_execution_path,
    )
    
    # Create all possible tasks
    generate_data = PythonOperator(
        task_id="generate_dummy_data",
        python_callable=generate_dummy_data,
        trigger_rule="none_failed",
    )
    
    run_pipeline = PythonOperator(
        task_id="run_dlt_pipeline",
        python_callable=run_dlt_pipeline,
        trigger_rule="none_failed",
    )
    
    generate_data_k8 = KubernetesPodOperator(
        task_id="generate_dummy_data_k8",
        namespace="default",
        image="python:3.11-slim",
        cmds=["bash", "-c"],
        arguments=[
            """
            pip install -r /opt/airflow/dags/../requirements.txt &&
            cd /opt/airflow/dags/../dummy &&
            python -c "
            import sys
            sys.path.append('/opt/airflow/dags/../dummy')
            from synthetic_data_generator import generate_synthetic_data, save_synthetic_data_to_duckdb

            tables = ['shopify.products']
            db_path = '/opt/airflow/dags/../../data.duckdb'
            synthetic_data = generate_synthetic_data(tables=tables, db_path=db_path, num_rows=1000)
            save_synthetic_data_to_duckdb(synthetic_data=synthetic_data, db_path=db_path, replace_existing=True)
            print('Synthetic data generated successfully')
            "
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
        trigger_rule="none_failed",
    )
    
    run_pipeline_k8 = KubernetesPodOperator(
        task_id="run_dlt_pipeline_k8",
        namespace="default",
        image="python:3.11-slim",
        cmds=["bash", "-c"],
        arguments=[
            """
            pip install -r /opt/airflow/dags/../requirements.txt &&
            cd /opt/airflow/dags/../dlt &&
            python -c "
            import sys
            sys.path.append('/opt/airflow/dags/../dlt')
            from pipelines.run_shopify_pipeline import run
            success = run()
            if not success:
                exit(1)
            print('Pipeline completed successfully')
            "
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
        trigger_rule="none_failed",
    )

    # Final task that all execution paths converge to
    end = EmptyOperator(
        task_id="end",
        trigger_rule="none_failed",
    )

    # Set task dependencies - decision task branches to the appropriate execution path
    start >> decision
    
    # Each execution path is controlled by the decision task
    decision >> [generate_data, run_pipeline, generate_data_k8, run_pipeline_k8]
    
    # All execution paths converge to the end task
    [generate_data, run_pipeline, generate_data_k8, run_pipeline_k8] >> end
