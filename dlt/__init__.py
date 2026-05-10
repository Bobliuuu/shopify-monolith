"""
Data Load Tool (DLT) package for Shopify data pipeline.

This package provides tools for extracting, transforming, and loading Shopify data
into various destinations including DuckDB.
"""

__version__ = "1.0.0"
__author__ = "Shopify Data Team"

# Import main components to make them available at package level
from .pipelines.run_shopify_pipeline import run as run_shopify_pipeline
from .sources.shopify_source import shopify_source

__all__ = [
    "run_shopify_pipeline",
    "shopify_source",
] 