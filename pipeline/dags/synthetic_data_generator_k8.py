#!/usr/bin/env python3
"""
Standalone script to generate synthetic Shopify data using SDV.
This file is executed in Kubernetes mode by the Airflow DAG.
"""

import sys
import os
from pathlib import Path

def main():
    """Main function to generate synthetic data"""
    try:
        print("🚀 Starting synthetic data generation in Kubernetes...")
        
        # Add the pipeline directory to Python path (relative to dags)
        pipeline_root = Path("/opt/airflow/dags").parent
        sys.path.append(str(pipeline_root))
        
        print(f"📁 Pipeline root: {pipeline_root}")
        print(f"🐍 Python path: {sys.path}")
        
        # Import the synthetic data generator
        from synthetic_data_generator import generate_synthetic_data, save_synthetic_data_to_duckdb
        
        print("📦 Synthetic data generator imported successfully")
        
        # Generate synthetic data
        tables = ["shopify.products"]
        db_path = str(pipeline_root.parent / "data.duckdb")  # ../../data.duckdb
        
        print(f"🗄️ Database path: {db_path}")
        
        synthetic_data = generate_synthetic_data(
            tables=tables,
            db_path=db_path,
            num_rows=1000,
        )
        
        # Save to DuckDB
        save_synthetic_data_to_duckdb(
            synthetic_data=synthetic_data,
            db_path=db_path,
            replace_existing=True,
        )
        
        print("✅ Synthetic data generated and saved successfully in Kubernetes!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"Python path: {sys.path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Data generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 