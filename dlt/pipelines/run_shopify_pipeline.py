#!/usr/bin/env python3
"""
Shopify DLT Pipeline

This module provides a data pipeline for extracting Shopify data using DLT.
It can be run as a standalone script or imported as a module.
"""

import dlt
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from pipelines._duckdb_path import MONOLITH_DUCKDB, REPO_ROOT

# Add the dlt sources to the path
dlt_root = Path(__file__).resolve().parent.parent
sys.path.append(str(dlt_root))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def run(record_metadata: bool = False, warehouse_run_id: str | None = None):
    """Run the Shopify DLT pipeline into ``data.duckdb`` schema ``shopify``."""
    ingestion_id = None
    con = None
    try:
        print("🚀 Starting Shopify DLT pipeline...")
        
        # Load environment variables
        load_dotenv()
        
        # Check required environment variables
        required_vars = ['SHOPIFY_API_KEY', 'SHOPIFY_API_PASSWORD', 'SHOPIFY_SHOP_NAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {missing_vars}")
            print("Please set these variables in your .env file or environment")
            return False
        
        print("✅ Environment variables loaded successfully")

        if record_metadata:
            import duckdb
            from warehouse.metadata import (
                apply_meta_schema,
                complete_ingestion_run,
                start_ingestion_run,
            )

            con = duckdb.connect(str(MONOLITH_DUCKDB))
            apply_meta_schema(con)
            if not warehouse_run_id:
                raise ValueError("warehouse_run_id required when record_metadata=True")
            ingestion_id = start_ingestion_run(con, warehouse_run_id, "shopify", "live")
        
        # Import the Shopify source
        from sources.shopify_source import shopify_source
        
        # Create the pipeline
        pipeline = dlt.pipeline(
            pipeline_name="shopify_data",
            destination=dlt.destinations.duckdb(str(MONOLITH_DUCKDB)),
            dataset_name="shopify",
        )
        
        print("📦 Pipeline created successfully")
        
        # Run the pipeline
        load_info = pipeline.run(shopify_source(), table_name="products")
        
        print("✅ Shopify pipeline completed successfully!")
        print(f"📊 Load info: {load_info}")

        if con is not None and ingestion_id:
            from warehouse.metadata import complete_ingestion_run

            rows = None
            try:
                rows = con.execute(
                    "SELECT COUNT(*) FROM shopify.shopify_products"
                ).fetchone()[0]
            except Exception:
                pass
            complete_ingestion_run(con, ingestion_id, rows_affected=int(rows or 0), status="completed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"Python path: {sys.path}")
        return False
    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        if con is not None and ingestion_id:
            from warehouse.metadata import complete_ingestion_run

            complete_ingestion_run(
                con,
                ingestion_id,
                status="failed",
                error_message=str(e),
            )
        return False
    finally:
        if con is not None:
            con.close()

def main():
    """Main function for standalone execution."""
    success = run()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
