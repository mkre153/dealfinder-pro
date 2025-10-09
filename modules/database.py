"""
Database Manager Module for DealFinder Pro
Provides comprehensive database operations with connection pooling,
error handling, and transaction management.

Supports: PostgreSQL, MySQL, SQLite
"""

import psycopg2
from psycopg2 import pool, extras, sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sqlite3
import mysql.connector
from mysql.connector import pooling
from typing import Dict, List, Optional, Any, Tuple
import logging
from contextlib import contextmanager
import os
import subprocess
from datetime import datetime, timedelta
import json

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass


class DatabaseManager:
    """
    Main database manager with connection pooling and transaction support.

    Supports multiple database backends:
    - PostgreSQL (recommended for production)
    - MySQL/MariaDB
    - SQLite (development/testing only)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize database manager with connection pooling.

        Args:
            config: Database configuration dictionary containing:
                - db_type: 'postgresql', 'mysql', or 'sqlite'
                - host: Database host (not needed for SQLite)
                - port: Database port
                - database: Database name
                - user: Database user
                - password: Database password
                - min_connections: Minimum pool size (default: 1)
                - max_connections: Maximum pool size (default: 5)
        """
        self.config = config
        self.db_type = config.get('db_type', 'postgresql').lower()
        self.pool = None

        logger.info(f"Initializing DatabaseManager with {self.db_type}")

        try:
            self._initialize_pool()
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

    def _initialize_pool(self):
        """Initialize connection pool based on database type"""
        min_conn = self.config.get('min_connections', 1)
        max_conn = self.config.get('max_connections', 5)

        if self.db_type == 'postgresql':
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                min_conn,
                max_conn,
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )

        elif self.db_type == 'mysql':
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="dealfinder_pool",
                pool_size=max_conn,
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )

        elif self.db_type == 'sqlite':
            # SQLite doesn't support traditional connection pooling
            self.db_path = self.config['database']
            logger.warning("SQLite mode - connection pooling limited")

        else:
            raise DatabaseError(f"Unsupported database type: {self.db_type}")

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections with automatic transaction handling.

        Automatically commits on success, rolls back on error.

        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)

        Yields:
            Database connection object
        """
        conn = None
        try:
            if self.db_type == 'postgresql':
                conn = self.pool.getconn()
            elif self.db_type == 'mysql':
                conn = self.pool.get_connection()
            elif self.db_type == 'sqlite':
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row  # Return rows as dictionaries

            yield conn

            # Commit transaction on success
            conn.commit()

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database transaction error: {e}")
            raise

        finally:
            if conn:
                if self.db_type == 'postgresql':
                    self.pool.putconn(conn)
                elif self.db_type == 'mysql':
                    conn.close()
                elif self.db_type == 'sqlite':
                    conn.close()

    def test_connection(self) -> bool:
        """
        Test database connectivity.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    # ========================================
    # PROPERTY OPERATIONS
    # ========================================

    def insert_property(self, property_data: Dict[str, Any]) -> int:
        """
        Insert new property or update if property_id already exists.

        Args:
            property_data: Dictionary containing property fields

        Returns:
            Property ID (database primary key)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Check if property exists
                if self.db_type == 'postgresql':
                    cursor.execute(
                        "SELECT id FROM properties WHERE property_id = %s",
                        (property_data.get('property_id'),)
                    )
                else:
                    cursor.execute(
                        "SELECT id FROM properties WHERE property_id = ?",
                        (property_data.get('property_id'),)
                    )

                existing = cursor.fetchone()

                if existing:
                    # Update existing property
                    property_id = existing[0]
                    self.update_property(property_data['property_id'], property_data)
                    logger.info(f"Updated existing property: {property_data['property_id']}")
                    return property_id

                # Insert new property
                columns = list(property_data.keys())
                values = [property_data[col] for col in columns]

                if self.db_type == 'postgresql':
                    placeholders = ', '.join(['%s'] * len(columns))
                    query = f"""
                        INSERT INTO properties ({', '.join(columns)})
                        VALUES ({placeholders})
                        RETURNING id
                    """
                    cursor.execute(query, values)
                    property_id = cursor.fetchone()[0]

                else:
                    placeholders = ', '.join(['?'] * len(columns))
                    query = f"""
                        INSERT INTO properties ({', '.join(columns)})
                        VALUES ({placeholders})
                    """
                    cursor.execute(query, values)
                    property_id = cursor.lastrowid

                cursor.close()
                logger.info(f"Inserted new property: {property_data['property_id']} (ID: {property_id})")
                return property_id

        except Exception as e:
            logger.error(f"Failed to insert property: {e}")
            raise DatabaseError(f"Property insertion failed: {e}")

    def update_property(self, property_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing property by property_id.

        Args:
            property_id: Unique property identifier
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Build UPDATE query
                set_clause = ', '.join([f"{key} = %s" if self.db_type == 'postgresql' else f"{key} = ?"
                                       for key in updates.keys()])
                values = list(updates.values())
                values.append(property_id)

                if self.db_type == 'postgresql':
                    query = f"UPDATE properties SET {set_clause} WHERE property_id = %s"
                else:
                    query = f"UPDATE properties SET {set_clause} WHERE property_id = ?"

                cursor.execute(query, values)
                rows_affected = cursor.rowcount
                cursor.close()

                logger.info(f"Updated property {property_id}: {rows_affected} row(s) affected")
                return rows_affected > 0

        except Exception as e:
            logger.error(f"Failed to update property {property_id}: {e}")
            raise DatabaseError(f"Property update failed: {e}")

    def get_property_by_id(self, property_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch single property by property_id.

        Args:
            property_id: Unique property identifier

        Returns:
            Property dictionary or None if not found
        """
        try:
            with self.get_connection() as conn:
                if self.db_type == 'postgresql':
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute("SELECT * FROM properties WHERE property_id = %s", (property_id,))
                else:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM properties WHERE property_id = ?", (property_id,))

                row = cursor.fetchone()
                cursor.close()

                if row:
                    if self.db_type == 'postgresql':
                        return dict(row)
                    else:
                        return dict(zip([col[0] for col in cursor.description], row))
                return None

        except Exception as e:
            logger.error(f"Failed to fetch property {property_id}: {e}")
            return None

    def get_properties_by_score(self, min_score: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch properties above score threshold.

        Args:
            min_score: Minimum opportunity score
            limit: Maximum number of results

        Returns:
            List of property dictionaries
        """
        try:
            with self.get_connection() as conn:
                if self.db_type == 'postgresql':
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute(
                        """
                        SELECT * FROM properties
                        WHERE opportunity_score >= %s
                        ORDER BY opportunity_score DESC, created_at DESC
                        LIMIT %s
                        """,
                        (min_score, limit)
                    )
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT * FROM properties
                        WHERE opportunity_score >= ?
                        ORDER BY opportunity_score DESC, created_at DESC
                        LIMIT ?
                        """,
                        (min_score, limit)
                    )
                    results = [dict(zip([col[0] for col in cursor.description], row))
                              for row in cursor.fetchall()]

                cursor.close()
                logger.info(f"Retrieved {len(results)} properties with score >= {min_score}")
                return results

        except Exception as e:
            logger.error(f"Failed to fetch properties by score: {e}")
            return []

    def get_properties_by_criteria(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Advanced property search with flexible criteria.

        Args:
            filters: Dictionary of search criteria
                - zip_code: Property ZIP code
                - property_type: Property type (Single Family, Condo, etc.)
                - bedrooms: Number of bedrooms
                - created_at_after: datetime or ISO string for date filtering
                - min_price: Minimum list price
                - max_price: Maximum list price

        Returns:
            List of matching property dictionaries
        """
        try:
            with self.get_connection() as conn:
                conditions = []
                values = []

                if 'zip_code' in filters:
                    conditions.append("zip_code = %s" if self.db_type == 'postgresql' else "zip_code = ?")
                    values.append(filters['zip_code'])

                if 'property_type' in filters:
                    conditions.append("property_type = %s" if self.db_type == 'postgresql' else "property_type = ?")
                    values.append(filters['property_type'])

                if 'bedrooms' in filters:
                    conditions.append("bedrooms = %s" if self.db_type == 'postgresql' else "bedrooms = ?")
                    values.append(filters['bedrooms'])

                if 'created_at_after' in filters:
                    conditions.append("created_at >= %s" if self.db_type == 'postgresql' else "created_at >= ?")
                    # Handle datetime or string
                    created_after = filters['created_at_after']
                    if isinstance(created_after, str):
                        values.append(created_after)
                    else:
                        values.append(created_after.isoformat())

                if 'min_price' in filters:
                    conditions.append("list_price >= %s" if self.db_type == 'postgresql' else "list_price >= ?")
                    values.append(filters['min_price'])

                if 'max_price' in filters:
                    conditions.append("list_price <= %s" if self.db_type == 'postgresql' else "list_price <= ?")
                    values.append(filters['max_price'])

                where_clause = " AND ".join(conditions) if conditions else "1=1"
                query = f"SELECT * FROM properties WHERE {where_clause} ORDER BY created_at DESC"

                if self.db_type == 'postgresql':
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute(query, values)
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    cursor = conn.cursor()
                    cursor.execute(query, values)
                    results = [dict(zip([col[0] for col in cursor.description], row))
                              for row in cursor.fetchall()]

                cursor.close()
                logger.info(f"Found {len(results)} properties matching criteria")
                return results

        except Exception as e:
            logger.error(f"Failed to search properties: {e}")
            return []

    def get_unsynced_properties(self) -> List[Dict[str, Any]]:
        """
        Get properties with pending GHL sync status.

        Returns:
            List of unsynced property dictionaries
        """
        try:
            with self.get_connection() as conn:
                if self.db_type == 'postgresql':
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute(
                        """
                        SELECT * FROM properties
                        WHERE ghl_sync_status = 'pending'
                          AND opportunity_score >= 75
                        ORDER BY opportunity_score DESC, created_at DESC
                        """
                    )
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT * FROM properties
                        WHERE ghl_sync_status = 'pending'
                          AND opportunity_score >= 75
                        ORDER BY opportunity_score DESC, created_at DESC
                        """
                    )
                    results = [dict(zip([col[0] for col in cursor.description], row))
                              for row in cursor.fetchall()]

                cursor.close()
                logger.info(f"Found {len(results)} unsynced properties")
                return results

        except Exception as e:
            logger.error(f"Failed to fetch unsynced properties: {e}")
            return []

    def mark_property_synced(self, property_id: str, ghl_opportunity_id: str) -> bool:
        """
        Mark property as successfully synced to GHL.

        Args:
            property_id: Property identifier
            ghl_opportunity_id: GHL opportunity ID

        Returns:
            True if successful
        """
        updates = {
            'ghl_opportunity_id': ghl_opportunity_id,
            'ghl_sync_status': 'synced',
            'ghl_sync_date': datetime.now()
        }
        return self.update_property(property_id, updates)

    def get_price_reductions(self, days_back: int = 1) -> List[Dict[str, Any]]:
        """
        Get properties with recent price reductions.

        Args:
            days_back: Number of days to look back

        Returns:
            List of properties with price reductions
        """
        try:
            with self.get_connection() as conn:
                cutoff_date = datetime.now() - timedelta(days=days_back)

                if self.db_type == 'postgresql':
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute(
                        """
                        SELECT * FROM properties
                        WHERE price_reduction_date >= %s
                          AND price_reduction_amount > 0
                        ORDER BY price_reduction_amount DESC
                        """,
                        (cutoff_date,)
                    )
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT * FROM properties
                        WHERE price_reduction_date >= ?
                          AND price_reduction_amount > 0
                        ORDER BY price_reduction_amount DESC
                        """,
                        (cutoff_date,)
                    )
                    results = [dict(zip([col[0] for col in cursor.description], row))
                              for row in cursor.fetchall()]

                cursor.close()
                logger.info(f"Found {len(results)} price reductions in last {days_back} day(s)")
                return results

        except Exception as e:
            logger.error(f"Failed to fetch price reductions: {e}")
            return []

    # ========================================
    # BUYER OPERATIONS
    # ========================================

    def upsert_buyer(self, buyer_data: Dict[str, Any]) -> int:
        """
        Insert or update buyer by ghl_contact_id.

        Args:
            buyer_data: Dictionary containing buyer fields

        Returns:
            Buyer ID (database primary key)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Check if buyer exists
                if self.db_type == 'postgresql':
                    cursor.execute(
                        "SELECT id FROM buyers WHERE ghl_contact_id = %s",
                        (buyer_data.get('ghl_contact_id'),)
                    )
                else:
                    cursor.execute(
                        "SELECT id FROM buyers WHERE ghl_contact_id = ?",
                        (buyer_data.get('ghl_contact_id'),)
                    )

                existing = cursor.fetchone()

                if existing:
                    # Update existing buyer
                    buyer_id = existing[0]
                    columns = [k for k in buyer_data.keys() if k != 'ghl_contact_id']
                    set_clause = ', '.join([f"{col} = %s" if self.db_type == 'postgresql' else f"{col} = ?"
                                           for col in columns])
                    values = [buyer_data[col] for col in columns]
                    values.append(buyer_data['ghl_contact_id'])

                    if self.db_type == 'postgresql':
                        query = f"UPDATE buyers SET {set_clause} WHERE ghl_contact_id = %s"
                    else:
                        query = f"UPDATE buyers SET {set_clause} WHERE ghl_contact_id = ?"

                    cursor.execute(query, values)
                    logger.info(f"Updated buyer: {buyer_data['ghl_contact_id']}")

                else:
                    # Insert new buyer
                    columns = list(buyer_data.keys())
                    values = [buyer_data[col] for col in columns]

                    if self.db_type == 'postgresql':
                        placeholders = ', '.join(['%s'] * len(columns))
                        query = f"""
                            INSERT INTO buyers ({', '.join(columns)})
                            VALUES ({placeholders})
                            RETURNING id
                        """
                        cursor.execute(query, values)
                        buyer_id = cursor.fetchone()[0]
                    else:
                        placeholders = ', '.join(['?'] * len(columns))
                        query = f"""
                            INSERT INTO buyers ({', '.join(columns)})
                            VALUES ({placeholders})
                        """
                        cursor.execute(query, values)
                        buyer_id = cursor.lastrowid

                    logger.info(f"Inserted new buyer: {buyer_data['ghl_contact_id']}")

                cursor.close()
                return buyer_id

        except Exception as e:
            logger.error(f"Failed to upsert buyer: {e}")
            raise DatabaseError(f"Buyer upsert failed: {e}")

    def get_active_buyers(self) -> List[Dict[str, Any]]:
        """
        Get all active buyers.

        Returns:
            List of active buyer dictionaries
        """
        try:
            with self.get_connection() as conn:
                if self.db_type == 'postgresql':
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute(
                        "SELECT * FROM buyers WHERE buyer_status = 'active' ORDER BY created_at DESC"
                    )
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT * FROM buyers WHERE buyer_status = 'active' ORDER BY created_at DESC"
                    )
                    results = [dict(zip([col[0] for col in cursor.description], row))
                              for row in cursor.fetchall()]

                cursor.close()
                logger.info(f"Retrieved {len(results)} active buyers")
                return results

        except Exception as e:
            logger.error(f"Failed to fetch active buyers: {e}")
            return []

    def get_buyers_by_criteria(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Advanced buyer search with flexible criteria.

        Args:
            filters: Dictionary of search criteria
                - min_budget: Minimum budget
                - max_budget: Maximum budget
                - buyer_status: Buyer status
                - sms_opt_in: SMS opt-in status

        Returns:
            List of matching buyer dictionaries
        """
        try:
            with self.get_connection() as conn:
                conditions = []
                values = []

                if 'min_budget' in filters:
                    conditions.append("min_budget >= %s" if self.db_type == 'postgresql' else "min_budget >= ?")
                    values.append(filters['min_budget'])

                if 'max_budget' in filters:
                    conditions.append("max_budget <= %s" if self.db_type == 'postgresql' else "max_budget <= ?")
                    values.append(filters['max_budget'])

                if 'buyer_status' in filters:
                    conditions.append("buyer_status = %s" if self.db_type == 'postgresql' else "buyer_status = ?")
                    values.append(filters['buyer_status'])

                if 'sms_opt_in' in filters:
                    conditions.append("sms_opt_in = %s" if self.db_type == 'postgresql' else "sms_opt_in = ?")
                    values.append(filters['sms_opt_in'])

                where_clause = " AND ".join(conditions) if conditions else "1=1"
                query = f"SELECT * FROM buyers WHERE {where_clause} ORDER BY created_at DESC"

                if self.db_type == 'postgresql':
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute(query, values)
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    cursor = conn.cursor()
                    cursor.execute(query, values)
                    results = [dict(zip([col[0] for col in cursor.description], row))
                              for row in cursor.fetchall()]

                cursor.close()
                logger.info(f"Found {len(results)} buyers matching criteria")
                return results

        except Exception as e:
            logger.error(f"Failed to search buyers: {e}")
            return []

    # ========================================
    # MATCH OPERATIONS
    # ========================================

    def insert_property_match(self, property_id: int, buyer_id: int, match_data: Dict[str, Any]) -> int:
        """
        Create property-buyer match record.

        Args:
            property_id: Property database ID
            buyer_id: Buyer database ID
            match_data: Match details (score, reasons, etc.)

        Returns:
            Match ID
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                match_data['property_id'] = property_id
                match_data['buyer_id'] = buyer_id

                columns = list(match_data.keys())
                values = [match_data[col] for col in columns]

                if self.db_type == 'postgresql':
                    placeholders = ', '.join(['%s'] * len(columns))
                    query = f"""
                        INSERT INTO property_matches ({', '.join(columns)})
                        VALUES ({placeholders})
                        ON CONFLICT (property_id, buyer_id)
                        DO UPDATE SET match_score = EXCLUDED.match_score,
                                     match_reasons = EXCLUDED.match_reasons
                        RETURNING id
                    """
                    cursor.execute(query, values)
                    match_id = cursor.fetchone()[0]
                else:
                    placeholders = ', '.join(['?'] * len(columns))
                    query = f"""
                        INSERT OR REPLACE INTO property_matches ({', '.join(columns)})
                        VALUES ({placeholders})
                    """
                    cursor.execute(query, values)
                    match_id = cursor.lastrowid

                cursor.close()
                logger.info(f"Created match: Property {property_id} <-> Buyer {buyer_id}")
                return match_id

        except Exception as e:
            logger.error(f"Failed to insert property match: {e}")
            raise DatabaseError(f"Match insertion failed: {e}")

    def get_matches_for_property(self, property_id: int) -> List[Dict[str, Any]]:
        """
        Get all matched buyers for a property.

        Args:
            property_id: Property database ID

        Returns:
            List of match dictionaries with buyer details
        """
        try:
            with self.get_connection() as conn:
                if self.db_type == 'postgresql':
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute(
                        """
                        SELECT pm.*, b.first_name, b.last_name, b.email, b.phone
                        FROM property_matches pm
                        JOIN buyers b ON pm.buyer_id = b.id
                        WHERE pm.property_id = %s
                        ORDER BY pm.match_score DESC
                        """,
                        (property_id,)
                    )
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT pm.*, b.first_name, b.last_name, b.email, b.phone
                        FROM property_matches pm
                        JOIN buyers b ON pm.buyer_id = b.id
                        WHERE pm.property_id = ?
                        ORDER BY pm.match_score DESC
                        """,
                        (property_id,)
                    )
                    results = [dict(zip([col[0] for col in cursor.description], row))
                              for row in cursor.fetchall()]

                cursor.close()
                return results

        except Exception as e:
            logger.error(f"Failed to fetch matches for property {property_id}: {e}")
            return []

    def update_match_actions(self, match_id: int, actions: Dict[str, Any]) -> bool:
        """
        Update match action tracking (SMS sent, workflow triggered, etc.).

        Args:
            match_id: Match database ID
            actions: Dictionary of action fields to update

        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                set_clause = ', '.join([f"{key} = %s" if self.db_type == 'postgresql' else f"{key} = ?"
                                       for key in actions.keys()])
                values = list(actions.values())
                values.append(match_id)

                if self.db_type == 'postgresql':
                    query = f"UPDATE property_matches SET {set_clause} WHERE id = %s"
                else:
                    query = f"UPDATE property_matches SET {set_clause} WHERE id = ?"

                cursor.execute(query, values)
                rows_affected = cursor.rowcount
                cursor.close()

                logger.info(f"Updated match {match_id} actions")
                return rows_affected > 0

        except Exception as e:
            logger.error(f"Failed to update match actions: {e}")
            return False

    # ========================================
    # SYNC LOGGING
    # ========================================

    def log_sync(self, sync_data: Dict[str, Any]) -> int:
        """
        Log synchronization operation.

        Args:
            sync_data: Sync log data including type, status, stats

        Returns:
            Log entry ID
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                columns = list(sync_data.keys())
                values = [sync_data[col] for col in columns]

                if self.db_type == 'postgresql':
                    placeholders = ', '.join(['%s'] * len(columns))
                    query = f"""
                        INSERT INTO sync_logs ({', '.join(columns)})
                        VALUES ({placeholders})
                        RETURNING id
                    """
                    cursor.execute(query, values)
                    log_id = cursor.fetchone()[0]
                else:
                    placeholders = ', '.join(['?'] * len(columns))
                    query = f"""
                        INSERT INTO sync_logs ({', '.join(columns)})
                        VALUES ({placeholders})
                    """
                    cursor.execute(query, values)
                    log_id = cursor.lastrowid

                cursor.close()
                logger.info(f"Logged sync operation: {sync_data.get('sync_type')} - {sync_data.get('status')}")
                return log_id

        except Exception as e:
            logger.error(f"Failed to log sync: {e}")
            raise DatabaseError(f"Sync logging failed: {e}")

    def get_recent_syncs(self, sync_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch recent sync history.

        Args:
            sync_type: Type of sync operation
            limit: Maximum number of results

        Returns:
            List of sync log dictionaries
        """
        try:
            with self.get_connection() as conn:
                if self.db_type == 'postgresql':
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute(
                        """
                        SELECT * FROM sync_logs
                        WHERE sync_type = %s
                        ORDER BY started_at DESC
                        LIMIT %s
                        """,
                        (sync_type, limit)
                    )
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT * FROM sync_logs
                        WHERE sync_type = ?
                        ORDER BY started_at DESC
                        LIMIT ?
                        """,
                        (sync_type, limit)
                    )
                    results = [dict(zip([col[0] for col in cursor.description], row))
                              for row in cursor.fetchall()]

                cursor.close()
                return results

        except Exception as e:
            logger.error(f"Failed to fetch sync history: {e}")
            return []

    # ========================================
    # MAINTENANCE OPERATIONS
    # ========================================

    def backup_database(self, backup_path: str) -> bool:
        """
        Create database backup using native tools.

        Args:
            backup_path: Full path for backup file

        Returns:
            True if successful
        """
        try:
            if self.db_type == 'postgresql':
                # Use pg_dump
                cmd = [
                    'pg_dump',
                    '-h', self.config.get('host', 'localhost'),
                    '-p', str(self.config.get('port', 5432)),
                    '-U', self.config['user'],
                    '-F', 'c',  # Custom format
                    '-f', backup_path,
                    self.config['database']
                ]

                env = os.environ.copy()
                env['PGPASSWORD'] = self.config['password']

                result = subprocess.run(cmd, env=env, capture_output=True, text=True)

                if result.returncode == 0:
                    logger.info(f"Database backup created: {backup_path}")
                    return True
                else:
                    logger.error(f"Backup failed: {result.stderr}")
                    return False

            elif self.db_type == 'sqlite':
                # Use SQLite backup API
                import shutil
                shutil.copy2(self.db_path, backup_path)
                logger.info(f"SQLite backup created: {backup_path}")
                return True

            else:
                logger.warning(f"Backup not implemented for {self.db_type}")
                return False

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

    def cleanup_old_records(self, retention_days: int = 365) -> Dict[str, int]:
        """
        Archive or delete old property records.

        Args:
            retention_days: Keep records newer than this many days

        Returns:
            Dictionary with cleanup statistics
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=retention_days)

                # Delete old properties (or move to archive table)
                if self.db_type == 'postgresql':
                    cursor.execute(
                        """
                        DELETE FROM properties
                        WHERE created_at < %s
                          AND ghl_sync_status != 'synced'
                        """,
                        (cutoff_date,)
                    )
                else:
                    cursor.execute(
                        """
                        DELETE FROM properties
                        WHERE created_at < ?
                          AND ghl_sync_status != 'synced'
                        """,
                        (cutoff_date,)
                    )

                properties_deleted = cursor.rowcount

                # Delete old sync logs
                if self.db_type == 'postgresql':
                    cursor.execute(
                        "DELETE FROM sync_logs WHERE started_at < %s",
                        (cutoff_date,)
                    )
                else:
                    cursor.execute(
                        "DELETE FROM sync_logs WHERE started_at < ?",
                        (cutoff_date,)
                    )

                logs_deleted = cursor.rowcount
                cursor.close()

                stats = {
                    'properties_deleted': properties_deleted,
                    'logs_deleted': logs_deleted
                }

                logger.info(f"Cleanup complete: {stats}")
                return stats

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {'properties_deleted': 0, 'logs_deleted': 0}

    def close(self):
        """Close all database connections and cleanup pool"""
        if self.pool:
            if self.db_type == 'postgresql':
                self.pool.closeall()
            logger.info("Database connection pool closed")
