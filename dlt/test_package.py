#!/usr/bin/env python3
"""
Test script to verify the DLT package is working correctly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all DLT components can be imported."""
    try:
        print("🧪 Testing DLT package imports...")
        
        # Test importing from the package
        from dlt.pipelines.run_shopify_pipeline import run
        print("✅ Successfully imported run function")
        
        from dlt.sources.shopify_source import shopify_source
        print("✅ Successfully imported shopify_source")
        
        # Test the main package import
        import dlt
        print("✅ Successfully imported dlt package")
        
        print("🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"Python path: {sys.path}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_pipeline_function():
    """Test that the pipeline function can be called (without running)."""
    try:
        print("🧪 Testing pipeline function...")
        
        from dlt.pipelines.run_shopify_pipeline import run
        
        # Check if the function exists and is callable
        if callable(run):
            print("✅ Pipeline function is callable")
            return True
        else:
            print("❌ Pipeline function is not callable")
            return False
            
    except Exception as e:
        print(f"❌ Error testing pipeline function: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting DLT package tests...")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test pipeline function
    function_ok = test_pipeline_function()
    
    if imports_ok and function_ok:
        print("🎉 All tests passed! DLT package is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1) 