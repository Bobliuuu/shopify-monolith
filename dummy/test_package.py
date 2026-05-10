#!/usr/bin/env python3
"""
Test script to verify the dummy package is working correctly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all dummy package components can be imported."""
    try:
        print("🧪 Testing dummy package imports...")
        
        # Test importing from the package
        from dummy.synthetic_data_generator import generate_synthetic_data, save_synthetic_data_to_duckdb
        print("✅ Successfully imported generate_synthetic_data function")
        print("✅ Successfully imported save_synthetic_data_to_duckdb function")
        
        # Test the main package import
        import dummy
        print("✅ Successfully imported dummy package")
        
        print("🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"Python path: {sys.path}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_functions():
    """Test that the functions are callable (without running)."""
    try:
        print("🧪 Testing package functions...")
        
        from dummy.synthetic_data_generator import generate_synthetic_data, save_synthetic_data_to_duckdb
        
        # Check if the functions exist and are callable
        if callable(generate_synthetic_data):
            print("✅ generate_synthetic_data function is callable")
        else:
            print("❌ generate_synthetic_data function is not callable")
            return False
            
        if callable(save_synthetic_data_to_duckdb):
            print("✅ save_synthetic_data_to_duckdb function is callable")
        else:
            print("❌ save_synthetic_data_to_duckdb function is not callable")
            return False
            
        return True
            
    except Exception as e:
        print(f"❌ Error testing functions: {e}")
        return False

def test_package_structure():
    """Test that the package structure is correct."""
    try:
        print("🧪 Testing package structure...")
        
        import dummy
        
        # Check if the package has the expected attributes
        if hasattr(dummy, 'generate_synthetic_data'):
            print("✅ Package has generate_synthetic_data attribute")
        else:
            print("❌ Package missing generate_synthetic_data attribute")
            return False
            
        if hasattr(dummy, 'save_synthetic_data_to_duckdb'):
            print("✅ Package has save_synthetic_data_to_duckdb attribute")
        else:
            print("❌ Package missing save_synthetic_data_to_duckdb attribute")
            return False
            
        return True
            
    except Exception as e:
        print(f"❌ Error testing package structure: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting dummy package tests...")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test functions
    functions_ok = test_functions()
    
    # Test package structure
    structure_ok = test_package_structure()
    
    if imports_ok and functions_ok and structure_ok:
        print("🎉 All tests passed! Dummy package is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1) 