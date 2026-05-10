-- Greenfield ingestion schema (Shopify Admin–aligned extracted entities + lineage)
-- Apply via greenfield.schema.apply_greenfield_schema()

CREATE SCHEMA IF NOT EXISTS greenfield;

CREATE TABLE IF NOT EXISTS greenfield.ingestion_batches (
    batch_id VARCHAR PRIMARY KEY,
    dataset_root VARCHAR NOT NULL,
    split_filter VARCHAR,
    eval_mode VARCHAR NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    doc_count INTEGER,
    status VARCHAR
);

CREATE TABLE IF NOT EXISTS greenfield.documents (
    doc_id VARCHAR PRIMARY KEY,
    doc_type VARCHAR,
    tx_id VARCHAR,
    invoice_no VARCHAR,
    customer VARCHAR,
    doc_date VARCHAR,
    total DOUBLE,
    dataset_root VARCHAR NOT NULL,
    raw_text_path VARCHAR,
    ground_truth_ocr_path VARCHAR,
    noisy_ocr_path VARCHAR,
    image_prompt_path VARCHAR,
    image_path VARCHAR,
    want_image BOOLEAN,
    split_name VARCHAR,
    image_sha256 VARCHAR,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS greenfield.ocr_runs (
    ocr_run_id VARCHAR PRIMARY KEY,
    doc_id VARCHAR NOT NULL,
    batch_id VARCHAR,
    ocr_engine VARCHAR,
    eval_mode VARCHAR NOT NULL,
    source_hash VARCHAR,
    raw_text TEXT,
    cleaned_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS greenfield.extracted_entities (
    extraction_id VARCHAR PRIMARY KEY,
    doc_id VARCHAR NOT NULL,
    batch_id VARCHAR,
    entities JSON,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shopify GraphQL–shaped product rows (from labels + OCR)
CREATE TABLE IF NOT EXISTS greenfield.extracted_products (
    extraction_id VARCHAR PRIMARY KEY,
    doc_id VARCHAR NOT NULL,
    batch_id VARCHAR,
    id VARCHAR,
    title VARCHAR,
    vendor VARCHAR,
    product_type VARCHAR,
    handle VARCHAR,
    status VARCHAR,
    variants JSON,
    body_html VARCHAR,
    tags VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    admin_graphql_api_id VARCHAR,
    _confidence DOUBLE,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order-shaped rows (invoice / retail docs)
CREATE TABLE IF NOT EXISTS greenfield.extracted_orders (
    extraction_id VARCHAR PRIMARY KEY,
    doc_id VARCHAR NOT NULL,
    batch_id VARCHAR,
    order_id VARCHAR,
    order_number BIGINT,
    customer_id VARCHAR,
    customer_name VARCHAR,
    source_tx_id VARCHAR,
    source_invoice_no VARCHAR,
    payment_ref VARCHAR,
    subtotal DOUBLE,
    discount_total DOUBLE,
    shipping_total DOUBLE,
    tax_total DOUBLE,
    grand_total DOUBLE,
    status VARCHAR,
    order_date VARCHAR,
    line_items JSON,
    admin_graphql_api_id VARCHAR,
    _confidence DOUBLE,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS greenfield.extracted_line_items (
    line_item_id VARCHAR PRIMARY KEY,
    extraction_id VARCHAR NOT NULL,
    doc_id VARCHAR NOT NULL,
    batch_id VARCHAR,
    sku VARCHAR,
    title VARCHAR,
    qty DOUBLE,
    unit VARCHAR,
    unit_price DOUBLE,
    line_total DOUBLE,
    category VARCHAR,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS greenfield.shopify_id_mapping (
    mapping_id VARCHAR PRIMARY KEY,
    entity_type VARCHAR NOT NULL,
    greenfield_key VARCHAR NOT NULL,
    shopify_gid VARCHAR,
    shopify_numeric_id VARCHAR,
    mapped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR
);
