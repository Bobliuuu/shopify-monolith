# Shopify Data Pipeline with Airflow

This directory contains Airflow DAGs for extracting data from Shopify APIs and loading it into DuckDB.

## Overview

The pipeline consists of multiple DAGs that extract different Shopify entities:
- **Products**: Product information, variants, and inventory
- **Orders**: Order data with line items and customer information

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Shopify API access (domain and access token)

### 2. Installation

```bash
# Navigate to the pipeline directory
cd pipieline

# Run the setup script
./setup_airflow.sh
```

### 3. Configuration

1. Copy the environment example file:
```bash
cp env.example .env
```

2. Edit `.env` with your Shopify credentials:
```bash
SHOPIFY_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_access_token_here
```

### 4. Start Airflow

```bash
# Activate virtual environment
source venv/bin/activate

# Start Airflow webserver (in one terminal)
airflow webserver --port 8080

# Start Airflow scheduler (in another terminal)
airflow scheduler
```

Access the Airflow UI at: http://localhost:8080
- Username: admin
- Password: admin

## DAGs Overview

### shopify_products_ingestion
- **Schedule**: Daily at 2 AM
- **Purpose**: Extracts product data from Shopify API
- **Output**: `shopify_products` table in DuckDB
- **Data**: Product details, variants, inventory, pricing

### shopify_orders_ingestion
- **Schedule**: Daily at 3 AM
- **Purpose**: Extracts order data from Shopify API
- **Output**: `shopify_orders` table in DuckDB
- **Data**: Order details, line items, customer info, fulfillment

### greenfield_ingestion_dag
- **DAG id**: `greenfield_ingestion_dag`
- **Purpose**: Reads a local GreenField dataset (manifest + optional images), runs OCR/cleaning modes, loads `greenfield` tables into project-root `data.duckdb`, and refreshes stub `shopify.*` tables if missing (for dbt joins).
- **Configuration**: Set `GREENFIELD_DATASET_ROOT` to your synced dataset directory (R2 layout mirrors local paths under your prefix). Optional overrides: DAG params `eval_mode`, `split`, `max_docs`, `dataset_root`, `duckdb_path`.

### commerce_warehouse_nightly
- **DAG id**: `commerce_warehouse_nightly`
- **Purpose**: Unified nightly batch — writes `meta.warehouse_run` / `meta.ingestion_run` lineage, runs Shopify (live DLT or synthetic SDV/bootstrap), Stripe (live DLT or synthetic), seeds GA4 / Google Ads / Customer.io / legacy stub tables, optional Greenfield corpus path, then runs dbt models tagged `core`.
- **Configuration**: DAG params / trigger conf: `shopify_data_mode`, `stripe_data_mode`, `allow_synthetic_fallback`, `stub_integrations`, `greenfield_dataset_root`, `greenfield_max_docs`, `run_dbt`, `dbt_select`.
- **CLI**: `PYTHONPATH=<repo-root> python -m warehouse.nightly_runner` with optional `NIGHTLY_CONF_JSON` env holding a JSON object of the same keys.

## Database Schema

### shopify_products
Contains flattened product and variant data with fields like:
- Product ID, title, vendor, type
- Variant information (SKU, price, inventory)
- Extraction timestamp for data lineage

### shopify_orders
Contains order and line item data with fields like:
- Order details (ID, status, pricing)
- Line item information (product, quantity, price)
- Customer and shipping information

## Data Flow

1. **Extract**: API calls to Shopify Admin API
2. **Transform**: Flatten and normalize data structure
3. **Load**: Insert into DuckDB tables with deduplication

## Monitoring

- Check Airflow UI for DAG execution status
- Monitor logs in Airflow UI for any errors
- Data quality checks can be added as additional tasks

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Shopify has rate limits. The DAGs handle pagination automatically.

2. **Authentication**: Ensure `SHOPIFY_DOMAIN` and `SHOPIFY_ACCESS_TOKEN` are correctly set.

3. **Database Connection**: Verify DuckDB file path is accessible.

### Logs
- Airflow task logs are available in the Airflow UI
- Check the "Logs" tab for each task execution

## Development

To add new DAGs:
1. Create new Python file in `dags/` directory
2. Follow the same pattern as existing DAGs
3. Test locally before deploying

## Security Notes

- Never commit `.env` file with real credentials
- Use environment variables for sensitive data
- Consider using Airflow connections for API credentials 