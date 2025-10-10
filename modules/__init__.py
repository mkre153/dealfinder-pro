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

# Optional imports (database features not required for basic scanning)
try:
    from .database import DatabaseManager, DatabaseError
    _database_available = True
except ImportError:
    DatabaseManager = None
    DatabaseError = Exception
    _database_available = False

try:
    from .schema_mapper import SchemaMapper, SchemaMapperError
except ImportError:
    SchemaMapper = None
    SchemaMapperError = Exception

try:
    from .sync_manager import SyncManager, SyncError
except ImportError:
    SyncManager = None
    SyncError = Exception

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
