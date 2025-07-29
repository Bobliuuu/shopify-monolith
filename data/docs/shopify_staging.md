{% docs shopify_staging_overview %}
# Shopify Staging Models

The staging models in the Shopify data pipeline handle data transformation and business logic application.

## Purpose
Staging models serve as the transformation layer that:
- Applies business logic and data transformations
- Implements data quality rules and validations
- Prepares data for consumption by marts models

## Data Flow
```
Base Models → Staging Models → Marts Models
```

## Key Features
- **Business logic application**: Implements core business rules
- **Data transformation**: Converts raw data into business-ready formats
- **Quality assurance**: Ensures data meets business requirements
- **Performance optimization**: Optimizes data structure for analytics
{% enddocs %}

{% docs stg_shopify_transactions %}
# stg_shopify_transactions

## Overview
Staging model for Shopify transactions that applies business logic and data transformations.

## Purpose
- Transforms raw transaction data into business-ready format
- Applies business rules and data quality standards
- Prepares data for fact table consumption

## Source
- References `{{ ref('shopify_transactions_base') }}`

## Key Transformations
- **Data standardization**: Ensures consistent data formats
- **Business logic**: Applies transaction-specific business rules
- **Quality checks**: Validates data meets business requirements

## Business Rules
- Transaction amounts must be positive
- Status values must be valid (pending, completed, failed)
- Payment methods must be recognized types
- Required fields must not be null

## Usage
This model is consumed by marts models for final business logic application and analytics.
{% enddocs %}

{% docs stg_transaction_id %}
Unique identifier for each transaction after staging transformations. Maintains referential integrity with base model.
{% enddocs %}

{% docs stg_order_id %}
Order identifier after staging transformations. Used for order-level analytics and reporting.
{% enddocs %}

{% docs stg_customer_id %}
Customer identifier after staging transformations. Enables customer analytics and segmentation.
{% enddocs %}

{% docs stg_transaction_status %}
Validated transaction status after business rule application. Ensures only valid status values are passed to marts.
{% enddocs %}

{% docs stg_payment_method %}
Validated payment method after business rule application. Ensures only recognized payment types are processed.
{% enddocs %}

{% docs stg_transaction_amount %}
Validated transaction amount after business rule application. Must be positive and within acceptable ranges.
{% enddocs %}

{% docs stg_tax_amount %}
Validated tax amount after business rule application. Must be non-negative and reasonable for the transaction amount.
{% enddocs %}

{% docs stg_shipping_amount %}
Validated shipping amount after business rule application. Must be non-negative and reasonable for the order.
{% enddocs %}

{% docs stg_currency %}
Validated currency code after business rule application. Currently all transactions must be USD.
{% enddocs %}

{% docs stg_created_at %}
Validated creation timestamp after business rule application. Must be a valid date and not in the future.
{% enddocs %}

{% docs stg_updated_at %}
Validated update timestamp after business rule application. Must be after or equal to created_at.
{% enddocs %}

{% docs stg_country_code %}
Validated country code after business rule application. Must be a recognized country code.
{% enddocs %}

{% docs stg_sales_channel %}
Validated sales channel after business rule application. Must be either 'online' or 'in_store'.
{% enddocs %}

{% docs stg_source_table %}
Source table identifier after staging transformations. Maintains data lineage for audit purposes.
{% enddocs %} 