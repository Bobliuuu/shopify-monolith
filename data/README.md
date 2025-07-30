# Shopify Monolith - dbt Project

This dbt project uses DuckDB as the data warehouse and is configured for Shopify transaction data analysis.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the project:
```bash
dbt deps
```

3. Run the models:
```bash
dbt run
```

4. Run tests:
```bash
dbt test
```

## Project Structure

- `models/staging/`: Raw data models and initial transformations
- `models/marts/`: Business-level models with calculated fields
- `models/schema.yml`: Model documentation and tests

## Models

### stg_shopify_transactions_base
Staging model that generates sample Shopify transaction data with the following columns:
- transaction_id: Unique transaction identifier
- order_id: Order identifier
- customer_id: Customer identifier
- transaction_status: Status (pending, completed, failed)
- payment_method: Payment method used
- transaction_amount: Transaction amount
- tax_amount: Tax amount
- shipping_amount: Shipping amount
- currency: Currency code
- created_at: Creation timestamp
- updated_at: Last update timestamp
- country_code: Country code
- sales_channel: Sales channel (online/in_store)

### shopify_transactions_base
Main transactions table with additional calculated fields:
- total_amount: Sum of transaction, tax, and shipping
- successful_amount: Amount for completed transactions only
- transaction_recency: Categorization of transaction age

## Target Configuration

The project is configured with two targets:
- `dev`: Development environment (default)
- `prod`: Production environment

To switch targets:
```bash
dbt run --target prod
```

## Database

The project uses DuckDB with the database file `shopify_monolith.duckdb` in the data directory. 