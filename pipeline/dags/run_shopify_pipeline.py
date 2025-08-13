#!/usr/bin/env python3
"""
Standalone script to run the Shopify DLT pipeline.
This file is executed in Kubernetes mode by the Airflow DAG.
"""

import sys
import os
from pathlib import Path

def main():
    """Main function to run the DLT pipeline"""
    try:
        print("🚀 Starting Shopify DLT pipeline in Kubernetes...")
        
        # Add the dlt directory to Python path (relative to dags)
        dlt_root = Path("/opt/airflow/dags").parent.parent / "dlt"
        sys.path.append(str(dlt_root))
        
        print(f"📁 DLT root: {dlt_root}")
        print(f"🐍 Python path: {sys.path}")
        
        # Import and run the DLT pipeline
        from pipelines.run_shopify_pipeline import run
        
        print("📦 DLT pipeline imported successfully")
        run()
        
        print("✅ Shopify DLT pipeline completed successfully in Kubernetes!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"Python path: {sys.path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 