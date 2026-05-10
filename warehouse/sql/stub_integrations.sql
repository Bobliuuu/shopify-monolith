-- Contract-first schemas for GA4, Google Ads, Customer.io (live DLT can replace contents later).
CREATE SCHEMA IF NOT EXISTS ga4;
CREATE SCHEMA IF NOT EXISTS google_ads;
CREATE SCHEMA IF NOT EXISTS customerio;

CREATE TABLE IF NOT EXISTS ga4.events (
    event_date DATE,
    event_name VARCHAR,
    user_pseudo_id VARCHAR,
    transaction_id VARCHAR,
    value DOUBLE,
    currency VARCHAR,
    items JSON,
    page_location VARCHAR,
    source_system VARCHAR DEFAULT 'ga4',
    ingestion_mode VARCHAR DEFAULT 'synthetic',
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ga4.pseudo_users (
    user_pseudo_id VARCHAR,
    first_seen_date DATE,
    source_system VARCHAR DEFAULT 'ga4',
    ingestion_mode VARCHAR DEFAULT 'synthetic',
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS google_ads.campaign_stats (
    campaign_id VARCHAR,
    campaign_name VARCHAR,
    date DATE,
    impressions BIGINT,
    clicks BIGINT,
    cost_micros BIGINT,
    conversions DOUBLE,
    source_system VARCHAR DEFAULT 'google_ads',
    ingestion_mode VARCHAR DEFAULT 'synthetic',
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customerio.deliveries (
    delivery_id VARCHAR,
    campaign_id VARCHAR,
    recipient_email VARCHAR,
    event_name VARCHAR,
    subject VARCHAR,
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    source_system VARCHAR DEFAULT 'customerio',
    ingestion_mode VARCHAR DEFAULT 'synthetic',
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customerio.profiles (
    cio_id VARCHAR,
    email VARCHAR,
    created_at TIMESTAMP,
    source_system VARCHAR DEFAULT 'customerio',
    ingestion_mode VARCHAR DEFAULT 'synthetic',
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE SCHEMA IF NOT EXISTS legacy;
CREATE TABLE IF NOT EXISTS legacy.orders_csv_stub (
    external_order_id VARCHAR,
    customer_email VARCHAR,
    order_total DOUBLE,
    currency VARCHAR,
    placed_at TIMESTAMP,
    raw_row JSON,
    source_system VARCHAR DEFAULT 'legacy',
    ingestion_mode VARCHAR DEFAULT 'synthetic',
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
