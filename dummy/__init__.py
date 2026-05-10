"""
Dummy data generation package for Shopify data pipeline.

This package provides tools for generating synthetic Shopify data using SDV
for testing and development purposes.
"""

__version__ = "1.0.0"
__author__ = "Shopify Data Team"

# Import main components to make them available at package level
from .synthetic_data_generator import generate_synthetic_data, save_synthetic_data_to_duckdb

__all__ = [
    "generate_synthetic_data",
    "save_synthetic_data_to_duckdb",
] 