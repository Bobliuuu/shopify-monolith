{% docs shopify_marts_overview %}
# Shopify Marts Models

The marts models in the Shopify data pipeline provide the final business-ready datasets for analytics and reporting.

## Purpose
Marts models serve as the presentation layer that:
- Implements final business logic and calculations
- Provides analytics-ready datasets
- Supports reporting and dashboard requirements

## Data Flow
```
Staging Models → Marts Models → Analytics & Reporting
```

## Key Features
- **Business metrics**: Calculates key performance indicators
- **Analytics optimization**: Structured for efficient querying
- **Reporting ready**: Formatted for dashboard consumption
- **Documentation**: Comprehensive business documentation
{% enddocs %}

{% docs fct_shopify_transactions %}
# fct_shopify_transactions

## Overview
Fact table for Shopify transactions with comprehensive business logic and calculated fields.

## Purpose
- Provides analytics-ready transaction data
- Implements business calculations and metrics
- Supports reporting and dashboard requirements

## Source
- References `{{ ref('stg_shopify_transactions') }}`

## Key Calculations

### Financial Metrics
- **total_amount**: `transaction_amount + tax_amount + shipping_amount`
- **successful_amount**: Amount for completed transactions only

### Business Categorizations
- **transaction_recency**: 
  - `recent`: Within 7 days
  - `recent_month`: Within 30 days  
  - `older`: More than 30 days
- **transaction_value_category**:
  - `high_value`: ≥ $1,000
  - `medium_value`: $500 - $999
  - `low_value`: < $500
- **payment_category**:
  - `card`: Credit card payments
  - `digital_wallet`: PayPal payments
  - `shop_pay`: Shop Pay payments

## Business Logic
- Only successful transactions contribute to revenue calculations
- Transaction value categories support customer segmentation
- Payment categories enable payment method analysis
- Recency categories support customer lifecycle analysis

## Usage
This model is consumed by:
- Business intelligence dashboards
- Customer analytics reports
- Revenue analysis tools
- Marketing campaign analysis

## Performance Considerations
- Indexed on `transaction_id` for unique lookups
- Partitioned by `created_at` for time-based queries
- Optimized for common analytical queries
{% enddocs %}

{% docs fct_transaction_id %}
Unique identifier for each transaction in the fact table. Primary key used for joins and lookups in analytics.
{% enddocs %}

{% docs fct_order_id %}
Order identifier linking transactions to orders. Enables order-level analytics and reporting.
{% enddocs %}

{% docs fct_customer_id %}
Customer identifier for customer analytics and segmentation. Enables customer journey analysis.
{% enddocs %}

{% docs fct_transaction_status %}
Final transaction status after all business logic application. Used for revenue calculations and reporting.
{% enddocs %}

{% docs fct_payment_method %}
Final payment method after business logic application. Used for payment method analysis and optimization.
{% enddocs %}

{% docs fct_transaction_amount %}
Base transaction amount used for revenue calculations and financial reporting.
{% enddocs %}

{% docs fct_tax_amount %}
Tax amount used for financial reporting and tax analysis.
{% enddocs %}

{% docs fct_shipping_amount %}
Shipping amount used for logistics analysis and cost optimization.
{% enddocs %}

{% docs fct_currency %}
Currency code for financial reporting and multi-currency analysis.
{% enddocs %}

{% docs fct_created_at %}
Transaction creation timestamp used for time-based analysis and reporting.
{% enddocs %}

{% docs fct_updated_at %}
Transaction update timestamp used for audit trails and change tracking.
{% enddocs %}

{% docs fct_country_code %}
Country code for geographic analysis and regional reporting.
{% enddocs %}

{% docs fct_sales_channel %}
Sales channel for channel performance analysis and optimization.
{% enddocs %}

{% docs fct_source_table %}
Source table identifier for data lineage and source-specific analysis.
{% enddocs %}

{% docs fct_total_amount %}
Calculated total amount including transaction, tax, and shipping. Primary metric for revenue reporting.
{% enddocs %}

{% docs fct_successful_amount %}
Amount for completed transactions only. Used for revenue calculations and financial reporting.
{% enddocs %}

{% docs fct_transaction_recency %}
Categorization of transaction age for customer lifecycle analysis:
- `recent`: Within 7 days
- `recent_month`: Within 30 days
- `older`: More than 30 days
{% enddocs %}

{% docs fct_transaction_value_category %}
Transaction value categorization for customer segmentation:
- `high_value`: ≥ $1,000
- `medium_value`: $500 - $999
- `low_value`: < $500
{% enddocs %}

{% docs fct_payment_category %}
Payment method categorization for payment analysis:
- `card`: Credit card payments
- `digital_wallet`: PayPal payments
- `shop_pay`: Shop Pay payments
{% enddocs %} 