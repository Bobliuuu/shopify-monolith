# Shopify Products DAG - Execution Modes

This Airflow DAG supports three different execution modes to handle various scenarios and environments.

## Configuration Flags

Set these flags at the top of `shopify_products_dag.py`:

```python
DEBUG_MODE = True      # True -> generate dummy data; False -> run DLT pipeline
K8_MODE = True         # True -> run in Kubernetes; False -> run locally
```

## Execution Modes

### 1. Local Debug Mode
```python
DEBUG_MODE = True
K8_MODE = False
```
- **What it does**: Generates synthetic Shopify product data using SDV locally
- **Where it runs**: In the Airflow worker process
- **Use case**: Local development and testing
- **Dependencies**: SDV, pandas, duckdb installed in Airflow worker environment

### 2. Local Production Mode
```python
DEBUG_MODE = False
K8_MODE = False
```
- **What it does**: Runs the actual Shopify DLT pipeline locally
- **Where it runs**: In the Airflow worker process
- **Use case**: Production runs when you have a stable local environment
- **Dependencies**: DLT, Shopify API credentials, all dependencies in Airflow worker

### 3. Kubernetes Debug Mode
```python
DEBUG_MODE = True
K8_MODE = True
```
- **What it does**: Generates synthetic data in an isolated Kubernetes pod
- **Where it runs**: In a fresh Python 3.11-slim container
- **Use case**: When local environment has compatibility issues (e.g., PyArrow crashes)
- **Dependencies**: Installed fresh in the pod from `../requirements.txt`

### 4. Kubernetes Production Mode
```python
DEBUG_MODE = False
K8_MODE = True
```
- **What it does**: Runs the DLT pipeline in an isolated Kubernetes pod
- **Where it runs**: In a fresh Python 3.11-slim container
- **Use case**: Production runs with guaranteed environment isolation
- **Dependencies**: Installed fresh in the pod from `../requirements.txt`

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
├── synthetic_data_generator.py           # Local synthetic data generator
└── dlt/                                  # DLT pipeline code
    └── pipelines/
        └── run_shopify_pipeline.py       # Original DLT pipeline
```

## Path Mapping

### Kubernetes Pod Paths:
- **DAGs**: `/opt/airflow/dags/` (mounted from PVC)
- **Requirements**: `/opt/airflow/dags/../requirements.txt`
- **Database**: `/opt/airflow/dags/../../data.duckdb`
- **Pipeline code**: `/opt/airflow/dags/../` (pipeline directory)

### Local Paths:
- **DAGs**: `pipeline/dags/`
- **Requirements**: `pipeline/requirements.txt`
- **Database**: `data.duckdb` (project root)
- **Pipeline code**: `pipeline/`

## Troubleshooting

### PyArrow Segmentation Fault
If you encounter PyArrow crashes in local mode:
1. Switch to Kubernetes mode (`K8_MODE = True`)
2. The fresh Python 3.11-slim container avoids compatibility issues
3. All dependencies are installed fresh in the isolated environment

### Import Errors in Kubernetes
If Kubernetes pods fail to import modules:
1. Check that `requirements.txt` includes all necessary packages
2. Verify the volume mount paths are correct
3. Check pod logs for detailed error messages

### Local vs Kubernetes Performance
- **Local mode**: Faster startup, shares environment
- **Kubernetes mode**: Slower startup (installs dependencies), guaranteed isolation

## Best Practices

1. **Development**: Use Local Debug Mode for quick iterations
2. **Testing**: Use Kubernetes Debug Mode to avoid environment issues
3. **Production**: Use Kubernetes Production Mode for reliability
4. **Fallback**: Keep Local Production Mode as backup if K8 is unavailable

## Current Configuration

The DAG is currently configured for:
- **DEBUG_MODE = True**: Generate synthetic data
- **K8_MODE = True**: Run in Kubernetes pods

This configuration will:
1. Run the synthetic data generation in a fresh Kubernetes pod
2. Install dependencies from `../requirements.txt`
3. Access the database at `../../data.duckdb`
4. Avoid PyArrow crashes by using an isolated Python 3.11 environment 