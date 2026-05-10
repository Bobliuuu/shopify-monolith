# Shopify Products DAG - Execution Modes

This Airflow DAG supports three different execution modes to handle various scenarios and environments.

## Configuration

The DAG uses **parameters** that can be set when triggering the DAG or have default values:

```python
# Default configuration in the DAG
params={
    "debug_mode": False,  # True -> generate dummy data; False -> run DLT pipeline
    "k8_mode": False,     # True -> run in Kubernetes; False -> run locally
}
```

## Execution Modes

### 1. Local Debug Mode
```python
# Set when triggering the DAG
debug_mode: True
k8_mode: False
```
- **What it does**: Generates synthetic Shopify product data using SDV locally
- **Where it runs**: In the Airflow worker process
- **Use case**: Local development and testing
- **Dependencies**: SDV, pandas, duckdb installed in Airflow worker environment

### 2. Local Production Mode (Default)
```python
# Default configuration
debug_mode: False
k8_mode: False
```
- **What it does**: Runs the actual Shopify DLT pipeline locally using the importable package
- **Where it runs**: In the Airflow worker process
- **Use case**: Production runs when you have a stable local environment
- **Dependencies**: DLT, Shopify API credentials, all dependencies in Airflow worker

### 3. Kubernetes Debug Mode
```python
# Set when triggering the DAG
debug_mode: True
k8_mode: True
```
- **What it does**: Generates synthetic data in an isolated Kubernetes pod
- **Where it runs**: In a fresh Python 3.11-slim container
- **Use case**: When local environment has compatibility issues (e.g., PyArrow crashes)
- **Dependencies**: Installed fresh in the pod from `../requirements.txt`

### 4. Kubernetes Production Mode
```python
# Set when triggering the DAG
debug_mode: False
k8_mode: True
```
- **What it does**: Runs the DLT pipeline in an isolated Kubernetes pod using the importable package
- **Where it runs**: In a fresh Python 3.11-slim container
- **Use case**: Production runs with guaranteed environment isolation
- **Dependencies**: Installed fresh in the pod from `../requirements.txt`

## How to Configure

### Option 1: Use Defaults (Recommended for Production)
The DAG will run in **Local Production Mode** by default:
- `debug_mode: False` - Run DLT pipeline
- `k8_mode: False` - Run locally

### Option 2: Trigger with Parameters
When manually triggering the DAG, you can override the defaults:

**For Local Debug Mode:**
```json
{
    "debug_mode": true,
    "k8_mode": false
}
```

**For Kubernetes Debug Mode:**
```json
{
    "debug_mode": true,
    "k8_mode": true
}
```

**For Kubernetes Production Mode:**
```json
{
    "debug_mode": false,
    "k8_mode": true
}
```

### Option 3: Programmatic Configuration
You can also set parameters programmatically when calling the DAG:

```python
from airflow.models import DagBag
dagbag = DagBag()
dag = dagbag.get_dag('shopify_products_dag')
dag.params["debug_mode"] = True
dag.params["k8_mode"] = False
```

## DLT Package Structure

The DLT folder is now a proper Python package with the following structure:

```
dlt/
├── __init__.py                    # Main package initialization
├── pipelines/
│   ├── __init__.py               # Pipelines subpackage
│   └── run_shopify_pipeline.py   # Main Shopify pipeline
├── sources/
│   ├── __init__.py               # Sources subpackage
│   └── shopify_source.py         # Shopify data source
└── test_package.py               # Package testing script
```

## Dummy Package Structure

The dummy folder is also a proper Python package:

```
dummy/
├── __init__.py                    # Main package initialization
├── synthetic_data_generator.py    # Synthetic data generator
└── test_package.py               # Package testing script
```

### Package Features:
- **Importable**: Can be imported as `from dummy import generate_synthetic_data, save_synthetic_data_to_duckdb`
- **Modular**: Each component is properly separated and importable
- **Testable**: Includes test script to verify package functionality
- **Environment-aware**: Automatically loads environment variables and checks requirements

## Kubernetes Requirements

To use Kubernetes mode, ensure you have:

1. **Kubernetes cluster** accessible to Airflow
2. **Persistent Volume Claim** named `airflow-dags-pvc` mounted at `/opt/airflow/dags`
3. **Kubernetes provider** installed: `pip install apache-airflow-providers-cncf-kubernetes`
4. **Proper RBAC permissions** for Airflow to create pods

## File Structure

```
pipeline/
├── dags/
│   ├── shopify_products_dag.py           # Main DAG file
│   ├── synthetic_data_generator_k8.py    # K8 synthetic data generator
│   ├── run_shopify_pipeline.py           # K8 DLT pipeline runner
│   └── README.md                         # This file
├── requirements.txt                       # Dependencies for K8 pods
└── dummy/                                # Dummy package (importable)
    ├── __init__.py                       # Package initialization
    ├── synthetic_data_generator.py       # Synthetic data generator
    └── test_package.py                   # Package testing
```

## Path Mapping

### Kubernetes Pod Paths:
- **DAGs**: `/opt/airflow/dags/` (mounted from PVC)
- **Requirements**: `/opt/airflow/dags/../requirements.txt`
- **Database**: `/opt/airflow/dags/../../data.duckdb`
- **DLT Package**: `/opt/airflow/dags/../dlt/` (importable package)
- **Dummy Package**: `/opt/airflow/dags/../dummy/` (importable package)

### Local Paths:
- **DAGs**: `pipeline/dags/`
- **Requirements**: `pipeline/requirements.txt`
- **Database**: `data.duckdb` (project root)
- **DLT Package**: `dlt/` (importable package)
- **Dummy Package**: `dummy/` (importable package)

## Testing the Packages

Before running the DAG, test both packages:

```bash
# Test DLT package
cd /path/to/shopify-monolith
python dlt/test_package.py

# Test dummy package
python dummy/test_package.py
```

## Troubleshooting

### Import Errors
If you encounter import errors:
1. **Test the packages**: Run the test scripts for both packages
2. **Check Python path**: Ensure the packages are in your Python path
3. **Verify structure**: Make sure all `__init__.py` files exist

### PyArrow Segmentation Fault
If you encounter PyArrow crashes in local mode:
1. Switch to Kubernetes mode (`k8_mode: true`)
2. The fresh Python 3.11-slim container avoids compatibility issues
3. All dependencies are installed fresh in the isolated environment

### Local vs Kubernetes Performance
- **Local mode**: Faster startup, shares environment, uses importable packages
- **Kubernetes mode**: Slower startup (installs dependencies), guaranteed isolation

## Best Practices

1. **Development**: Use Local Debug Mode for quick iterations
2. **Testing**: Use Kubernetes Debug Mode to avoid environment issues
3. **Production**: Use Local Production Mode (default) with importable packages for reliability
4. **Fallback**: Use Kubernetes Production Mode if local environment has issues

## Current Configuration

The DAG is currently configured with **defaults**:
- **debug_mode: False**: Run DLT pipeline (not generate dummy data)
- **k8_mode: False**: Run locally (not in Kubernetes)

This configuration will:
1. Import the DLT package locally
2. Run the Shopify pipeline using the importable `run` function
3. Use the local environment with all dependencies
4. Provide better error handling and logging

## Quick Start

1. **Default run**: The DAG will run in Local Production Mode automatically
2. **Debug mode**: Trigger with `{"debug_mode": true, "k8_mode": false}`
3. **Kubernetes mode**: Trigger with `{"debug_mode": false, "k8_mode": true}`
4. **Full debug**: Trigger with `{"debug_mode": true, "k8_mode": true}` 

## Synthetic Dataset in Cloudflare R2

The synthetic generator now supports maximal Ambrook-style + Shopify data generation and uploads the full dataset tree to Cloudflare R2.

### Required environment variables

- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET`
- One of:
  - `R2_ENDPOINT_URL`, or
  - `R2_ACCOUNT_ID` (the generator derives `https://<account>.r2.cloudflarestorage.com`)

### Generator usage

```bash
python scripts/generator.py \
  --scale-profile maximal \
  --strict-plausibility \
  --dry-run \
  --upload-r2 \
  --r2-bucket "$R2_BUCKET" \
  --r2-prefix "datasets/greenfield/$(date +%Y%m%d)"
```

### R2 object layout contract

The upload mirrors local output paths under the selected prefix, for example:

- `raw/company/*`
- `raw/transactions/*`
- `raw/retail/*`
- `raw/artifacts/*`
- `labels/*`
- `ocr/*`
- `manifests/*`
- `docs/*`
- `images/*`

Use `manifests/r2_manifest.jsonl` and `manifests/r2_upload_summary.json` as the source of truth for downstream ingestion.