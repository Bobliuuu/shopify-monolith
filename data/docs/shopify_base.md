{% docs shopify_base_overview %}
# Shopify Base Models

The base models in the Shopify data pipeline handle the initial data processing and combination of multiple source tables.

## Purpose
Base models serve as the foundation layer that:
- Combines multiple source tables into unified datasets
- Performs initial data cleaning and standardization
- Provides a single source of truth for downstream models

## Data Flow
```
Source Tables → Base Models → Staging Models → Marts Models
```

## Key Features
- **Multi-source aggregation**: Combines data from multiple source tables
- **Source tracking**: Maintains traceability to original data sources
- **Data standardization**: Ensures consistent data formats across sources
- **Initial validation**: Basic data quality checks and constraints
{% enddocs %}

{% docs shopify_transactions_base %}
# shopify_transactions_base

## Overview
Base model that combines multiple Shopify transaction source tables into a unified dataset.

## Purpose
- Aggregates transaction data from multiple source systems
- Provides standardized transaction data for downstream processing
- Maintains source table traceability

## Source Tables
- `shopify_raw.transactions_table_1` - Primary transaction source
- `shopify_raw.transactions_table_2` - Secondary transaction source

## Key Columns
- `transaction_id`: Unique transaction identifier
- `source_table`: Tracks which source table the record came from
- `transaction_status`: Standardized status values
- `payment_method`: Normalized payment method categories

## Business Logic
- Combines data using UNION ALL to preserve all records
- Adds source tracking for data lineage
- Maintains original data structure for flexibility

## Usage
This model is referenced by staging models for further processing and business logic application.
{% enddocs %}

{% docs transaction_id %}
Unique identifier for each transaction. Used as the primary key for transaction records and ensures no duplicate transactions exist in the system.
{% enddocs %}

{% docs order_id %}
Identifier linking the transaction to a specific order. Allows tracking of multiple transactions per order and order-level analytics.
{% enddocs %}

{% docs customer_id %}
Identifier for the customer who made the transaction. Enables customer-level analytics and customer journey tracking.
{% enddocs %}

{% docs transaction_status %}
Current status of the transaction. Valid values are:
- `pending`: Transaction is being processed
- `completed`: Transaction was successful
- `failed`: Transaction failed to process
{% enddocs %}

{% docs payment_method %}
Method of payment used for the transaction. Valid values are:
- `credit_card`: Traditional credit/debit card payment
- `paypal`: PayPal digital wallet payment
- `shop_pay`: Shopify's installment payment option
{% enddocs %}

{% docs transaction_amount %}
The base amount of the transaction before taxes and shipping. This is the core transaction value used for revenue calculations.
{% enddocs %}

{% docs tax_amount %}
Tax amount applied to the transaction. Varies by location and product type.
{% enddocs %}

{% docs shipping_amount %}
Shipping cost for the transaction. May vary based on shipping method and destination.
{% enddocs %}

{% docs currency %}
Currency code for the transaction amount. Currently all transactions are in USD.
{% enddocs %}

{% docs created_at %}
Timestamp when the transaction was first created in the system.
{% enddocs %}

{% docs updated_at %}
Timestamp when the transaction was last modified in the system.
{% enddocs %}

{% docs country_code %}
Country code where the transaction occurred. Used for geographic analysis and tax calculations.
{% enddocs %}

{% docs sales_channel %}
Channel through which the sale was made. Valid values are:
- `online`: E-commerce website sales
- `in_store`: Physical store sales
{% enddocs %}

{% docs source_table %}
Identifier for the source table that provided this record. Enables data lineage tracking and source-specific analysis.
{% enddocs %} 