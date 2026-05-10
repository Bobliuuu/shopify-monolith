"""
DLT pipelines package.

Contains various data pipeline implementations for different data sources.
"""

from .run_shopify_pipeline import run as run_shopify_pipeline

__all__ = ["run_shopify_pipeline"]
