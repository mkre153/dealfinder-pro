"""
DealFinder Pro - Core Modules Package

This package contains all core modules for DealFinder Pro:
- scraper: Realtor.com scraping using HomeHarvest
- data_enrichment: Data merging, deduplication, and validation
- database: Database connection and operations management
- schema_mapper: Field mapping between external sources and internal schema
- sync_manager: Bidirectional sync with GoHighLevel CRM
"""

from .scraper import RealtorScraper
from .data_enrichment import DataEnrichment
from .database import DatabaseManager, DatabaseError
from .schema_mapper import SchemaMapper, SchemaMapperError
from .sync_manager import SyncManager, SyncError

__all__ = [
    'RealtorScraper',
    'DataEnrichment',
    'DatabaseManager',
    'DatabaseError',
    'SchemaMapper',
    'SchemaMapperError',
    'SyncManager',
    'SyncError'
]

__version__ = '1.0.0'
