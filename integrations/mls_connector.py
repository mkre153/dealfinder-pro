import pyodbc
import psycopg2
import psycopg2.extras
import mysql.connector
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

class MLSConnector:
    """Connects to MLS databases (SQL Server, PostgreSQL, MySQL)"""

    def __init__(self, config: Dict):
        self.config = config
        mls_config = config.get('mls_database', {})
        self.db_type = mls_config.get('type', 'sqlserver').lower()
        self.connection = None
        self.logger = logging.getLogger(__name__)

        # Database connection parameters
        self.host = mls_config.get('host', 'localhost')
        self.port = mls_config.get('port')
        self.database = mls_config.get('database')
        self.username = mls_config.get('username')
        self.password = mls_config.get('password')
        self.table_name = mls_config.get('table_name', 'Listings')

        # Query templates
        self.query_template = mls_config.get('query_template')

        self.logger.info("MLSConnector initialized for database type: %s", self.db_type)

    def connect(self) -> bool:
        """
        Establish connection based on database type.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.db_type == 'sqlserver':
                self._connect_sqlserver()
            elif self.db_type == 'postgresql':
                self._connect_postgresql()
            elif self.db_type == 'mysql':
                self._connect_mysql()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")

            self.logger.info("Successfully connected to %s database", self.db_type)
            return True

        except Exception as e:
            self.logger.error("Failed to connect to %s database: %s", self.db_type, str(e))
            return False

    def _connect_sqlserver(self):
        """Connect to SQL Server using pyodbc"""
        # Build connection string
        if self.port:
            server = f"{self.host},{self.port}"
        else:
            server = self.host

        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password}"
        )

        self.connection = pyodbc.connect(conn_str)
        self.logger.debug("SQL Server connection established")

    def _connect_postgresql(self):
        """Connect to PostgreSQL using psycopg2"""
        conn_params = {
            'host': self.host,
            'database': self.database,
            'user': self.username,
            'password': self.password
        }

        if self.port:
            conn_params['port'] = self.port

        self.connection = psycopg2.connect(**conn_params)
        self.logger.debug("PostgreSQL connection established")

    def _connect_mysql(self):
        """Connect to MySQL using mysql.connector"""
        conn_params = {
            'host': self.host,
            'database': self.database,
            'user': self.username,
            'password': self.password
        }

        if self.port:
            conn_params['port'] = self.port

        self.connection = mysql.connector.connect(**conn_params)
        self.logger.debug("MySQL connection established")

    def test_connection(self) -> bool:
        """
        Verify connection works by executing simple query.

        Returns:
            True if connection is working
        """
        if not self.connection:
            self.logger.error("No active connection to test")
            return False

        try:
            cursor = self.connection.cursor()

            # Simple test query based on database type
            if self.db_type == 'sqlserver':
                cursor.execute("SELECT 1")
            elif self.db_type == 'postgresql':
                cursor.execute("SELECT 1")
            elif self.db_type == 'mysql':
                cursor.execute("SELECT 1")

            cursor.fetchone()
            cursor.close()

            self.logger.info("Database connection test successful")
            return True

        except Exception as e:
            self.logger.error("Database connection test failed: %s", str(e))
            return False

    def fetch_new_listings(self, hours_back: int = 24) -> List[Dict]:
        """
        Query listings modified within the specified time window.

        Args:
            hours_back: Number of hours to look back for new/modified listings

        Returns:
            List of property dictionaries
        """
        if not self.connection:
            raise RuntimeError("Database connection not established. Call connect() first.")

        try:
            # Calculate timestamp threshold
            threshold = datetime.now() - timedelta(hours=hours_back)

            # Use custom query template if provided, otherwise use default
            if self.query_template:
                query = self.query_template
                params = (threshold,)
            else:
                # Default query
                query = f"""
                    SELECT * FROM {self.table_name}
                    WHERE ModificationTimestamp > ?
                    ORDER BY ModificationTimestamp DESC
                """
                params = (threshold,)

            self.logger.info("Fetching listings modified in last %d hours", hours_back)
            results = self.execute_custom_query(query, params)

            self.logger.info("Fetched %d new/modified listings", len(results))
            return results

        except Exception as e:
            self.logger.error("Failed to fetch new listings: %s", str(e))
            raise

    def fetch_by_mls_numbers(self, mls_numbers: List[str]) -> List[Dict]:
        """
        Fetch specific listings by MLS ID numbers.

        Args:
            mls_numbers: List of MLS ID numbers

        Returns:
            List of property dictionaries
        """
        if not self.connection:
            raise RuntimeError("Database connection not established. Call connect() first.")

        if not mls_numbers:
            return []

        try:
            # Build parameterized query with IN clause
            placeholders = ','.join(['?'] * len(mls_numbers))
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE ListingKey IN ({placeholders})
            """

            self.logger.info("Fetching %d listings by MLS numbers", len(mls_numbers))
            results = self.execute_custom_query(query, tuple(mls_numbers))

            self.logger.info("Fetched %d listings", len(results))
            return results

        except Exception as e:
            self.logger.error("Failed to fetch listings by MLS numbers: %s", str(e))
            raise

    def fetch_price_changes(self, days_back: int = 7) -> List[Dict]:
        """
        Fetch properties with recent price reductions.

        Args:
            days_back: Number of days to look back for price changes

        Returns:
            List of property dictionaries with price changes
        """
        if not self.connection:
            raise RuntimeError("Database connection not established. Call connect() first.")

        try:
            threshold = datetime.now() - timedelta(days=days_back)

            # Query for properties with price changes
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE PriceChangeTimestamp > ?
                AND OriginalListPrice > ListPrice
                ORDER BY PriceChangeTimestamp DESC
            """

            params = (threshold,)

            self.logger.info("Fetching price changes from last %d days", days_back)
            results = self.execute_custom_query(query, params)

            self.logger.info("Fetched %d listings with price changes", len(results))
            return results

        except Exception as e:
            self.logger.error("Failed to fetch price changes: %s", str(e))
            raise

    def execute_custom_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Execute custom SQL query with parameterization.

        Args:
            query: SQL query string (use ? for parameters)
            params: Tuple of parameter values

        Returns:
            List of dictionaries (column_name: value)
        """
        if not self.connection:
            raise RuntimeError("Database connection not established. Call connect() first.")

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Execute parameterized query (prevents SQL injection)
            if params:
                # Convert ? to %s for PostgreSQL and MySQL
                if self.db_type in ('postgresql', 'mysql'):
                    query = query.replace('?', '%s')
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Fetch column names
            if self.db_type == 'sqlserver':
                columns = [column[0] for column in cursor.description]
            elif self.db_type == 'postgresql':
                columns = [desc[0] for desc in cursor.description]
            elif self.db_type == 'mysql':
                columns = [column[0] for column in cursor.description]

            # Fetch all rows
            rows = cursor.fetchall()

            # Convert to list of dictionaries
            results = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    value = row[i]
                    # Convert datetime objects to ISO format strings
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[column] = value
                results.append(row_dict)

            self.logger.debug("Query returned %d rows", len(results))
            return results

        except Exception as e:
            self.logger.error("Query execution failed: %s", str(e))
            self.logger.error("Query: %s", query)
            raise

        finally:
            if cursor:
                cursor.close()

    def close(self):
        """Close database connection"""
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("Database connection closed")
            except Exception as e:
                self.logger.error("Error closing database connection: %s", str(e))
            finally:
                self.connection = None
        else:
            self.logger.warning("No active connection to close")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
