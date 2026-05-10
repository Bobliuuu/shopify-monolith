-- Warehouse lineage and run tracking (single DuckDB contract: project-root data.duckdb)
CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE IF NOT EXISTS meta.warehouse_run (
    run_id VARCHAR PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR NOT NULL DEFAULT 'running',
    git_sha VARCHAR,
    airflow_dag_id VARCHAR,
    airflow_run_id VARCHAR,
    params_json JSON,
    notes VARCHAR
);

CREATE TABLE IF NOT EXISTS meta.ingestion_run (
    ingestion_id VARCHAR PRIMARY KEY,
    warehouse_run_id VARCHAR NOT NULL,
    integration VARCHAR NOT NULL,
    ingestion_mode VARCHAR NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR NOT NULL DEFAULT 'running',
    rows_affected BIGINT,
    error_message VARCHAR,
    detail_json JSON
);

CREATE INDEX IF NOT EXISTS idx_ingestion_run_warehouse ON meta.ingestion_run(warehouse_run_id);
CREATE INDEX IF NOT EXISTS idx_ingestion_run_integration ON meta.ingestion_run(integration);
