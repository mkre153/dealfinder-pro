"""
Client Database Module
Manages clients, search criteria, active agents, and match history using SQLite
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class ClientDatabase:
    """SQLite database for client and agent management"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file (default: database/clients.db)
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'database' / 'clients.db'

        self.db_path = str(db_path)
        self.conn = None
        self._init_database()

    def _init_database(self):
        """Create database and tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        cursor = self.conn.cursor()

        # Clients table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            notes TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)

        # Search criteria table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_criteria (
            criteria_id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            zip_codes TEXT,
            price_min INTEGER,
            price_max INTEGER,
            bedrooms_min INTEGER,
            bathrooms_min INTEGER,
            property_types TEXT,
            deal_quality TEXT,
            min_score INTEGER,
            investment_type TEXT,
            timeline TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        )
        """)

        # Active agents table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_agents (
            agent_id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            criteria_id TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            notification_email INTEGER DEFAULT 1,
            notification_sms INTEGER DEFAULT 0,
            notification_chat INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            last_check TEXT,
            matches_found INTEGER DEFAULT 0,
            paused_at TEXT,
            completed_at TEXT,
            cancelled_at TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(client_id),
            FOREIGN KEY (criteria_id) REFERENCES search_criteria(criteria_id)
        )
        """)

        # Agent matches table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_matches (
            match_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            property_address TEXT NOT NULL,
            property_data TEXT,
            matched_at TEXT NOT NULL,
            notified INTEGER DEFAULT 0,
            notified_at TEXT,
            status TEXT DEFAULT 'new',
            FOREIGN KEY (agent_id) REFERENCES active_agents(agent_id)
        )
        """)

        # Add ghl_contact_id column if it doesn't exist (migration)
        try:
            cursor.execute("ALTER TABLE clients ADD COLUMN ghl_contact_id TEXT")
        except sqlite3.OperationalError:
            # Column already exists
            pass

        self.conn.commit()

    # ===== CLIENT OPERATIONS =====

    def create_client(self, name: str, email: Optional[str] = None,
                     phone: Optional[str] = None, notes: Optional[str] = None) -> str:
        """Create a new client"""
        client_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO clients (client_id, name, email, phone, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (client_id, name, email, phone, notes, now, now))

        self.conn.commit()
        return client_id

    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get client by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_clients(self, status: Optional[str] = None) -> List[Dict]:
        """Get all clients, optionally filtered by status"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * FROM clients WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM clients ORDER BY created_at DESC")

        return [dict(row) for row in cursor.fetchall()]

    def update_client(self, client_id: str, **kwargs):
        """Update client fields"""
        kwargs['updated_at'] = datetime.now().isoformat()

        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [client_id]

        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE clients SET {fields} WHERE client_id = ?", values)
        self.conn.commit()

    # ===== SEARCH CRITERIA OPERATIONS =====

    def create_search_criteria(self, client_id: str, **kwargs) -> str:
        """Create search criteria for a client"""
        criteria_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # Convert lists to JSON strings
        if 'zip_codes' in kwargs and isinstance(kwargs['zip_codes'], list):
            kwargs['zip_codes'] = json.dumps(kwargs['zip_codes'])
        if 'property_types' in kwargs and isinstance(kwargs['property_types'], list):
            kwargs['property_types'] = json.dumps(kwargs['property_types'])
        if 'deal_quality' in kwargs and isinstance(kwargs['deal_quality'], list):
            kwargs['deal_quality'] = json.dumps(kwargs['deal_quality'])

        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO search_criteria (
            criteria_id, client_id, zip_codes, price_min, price_max,
            bedrooms_min, bathrooms_min, property_types, deal_quality,
            min_score, investment_type, timeline, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            criteria_id, client_id,
            kwargs.get('zip_codes'),
            kwargs.get('price_min'),
            kwargs.get('price_max'),
            kwargs.get('bedrooms_min'),
            kwargs.get('bathrooms_min'),
            kwargs.get('property_types'),
            kwargs.get('deal_quality'),
            kwargs.get('min_score'),
            kwargs.get('investment_type'),
            kwargs.get('timeline'),
            now
        ))

        self.conn.commit()
        return criteria_id

    def get_search_criteria(self, criteria_id: str) -> Optional[Dict]:
        """Get search criteria by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM search_criteria WHERE criteria_id = ?", (criteria_id,))
        row = cursor.fetchone()

        if not row:
            return None

        criteria = dict(row)

        # Parse JSON fields back to lists
        if criteria.get('zip_codes'):
            criteria['zip_codes'] = json.loads(criteria['zip_codes'])
        if criteria.get('property_types'):
            criteria['property_types'] = json.loads(criteria['property_types'])
        if criteria.get('deal_quality'):
            criteria['deal_quality'] = json.loads(criteria['deal_quality'])

        return criteria

    # ===== AGENT OPERATIONS =====

    def create_agent(self, client_id: str, criteria_id: str,
                    notification_email: bool = True,
                    notification_sms: bool = False,
                    notification_chat: bool = True) -> str:
        """Create a new search agent"""
        agent_id = str(uuid.uuid4())[:8].upper()  # Short readable ID
        now = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO active_agents (
            agent_id, client_id, criteria_id, status,
            notification_email, notification_sms, notification_chat,
            created_at
        ) VALUES (?, ?, ?, 'active', ?, ?, ?, ?)
        """, (agent_id, client_id, criteria_id,
              1 if notification_email else 0,
              1 if notification_sms else 0,
              1 if notification_chat else 0,
              now))

        self.conn.commit()
        return agent_id

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent by ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT a.*, c.name as client_name, s.*
        FROM active_agents a
        JOIN clients c ON a.client_id = c.client_id
        JOIN search_criteria s ON a.criteria_id = s.criteria_id
        WHERE a.agent_id = ?
        """, (agent_id,))

        row = cursor.fetchone()
        if not row:
            return None

        agent = dict(row)

        # Parse JSON fields
        if agent.get('zip_codes'):
            agent['zip_codes'] = json.loads(agent['zip_codes'])
        if agent.get('property_types'):
            agent['property_types'] = json.loads(agent['property_types'])
        if agent.get('deal_quality'):
            agent['deal_quality'] = json.loads(agent['deal_quality'])

        return agent

    def get_active_agents(self, client_id: Optional[str] = None) -> List[Dict]:
        """Get all active agents, optionally filtered by client"""
        cursor = self.conn.cursor()

        if client_id:
            cursor.execute("""
            SELECT a.*, c.name as client_name
            FROM active_agents a
            JOIN clients c ON a.client_id = c.client_id
            WHERE a.client_id = ? AND a.status = 'active'
            ORDER BY a.created_at DESC
            """, (client_id,))
        else:
            cursor.execute("""
            SELECT a.*, c.name as client_name
            FROM active_agents a
            JOIN clients c ON a.client_id = c.client_id
            WHERE a.status = 'active'
            ORDER BY a.created_at DESC
            """)

        return [dict(row) for row in cursor.fetchall()]

    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status (active, paused, completed, cancelled)"""
        timestamp_field = None
        if status == 'paused':
            timestamp_field = 'paused_at'
        elif status == 'completed':
            timestamp_field = 'completed_at'
        elif status == 'cancelled':
            timestamp_field = 'cancelled_at'

        cursor = self.conn.cursor()
        if timestamp_field:
            cursor.execute(f"""
            UPDATE active_agents
            SET status = ?, {timestamp_field} = ?
            WHERE agent_id = ?
            """, (status, datetime.now().isoformat(), agent_id))
        else:
            cursor.execute("UPDATE active_agents SET status = ? WHERE agent_id = ?",
                         (status, agent_id))

        self.conn.commit()

    def update_agent_last_check(self, agent_id: str):
        """Update agent's last check timestamp"""
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE active_agents SET last_check = ? WHERE agent_id = ?
        """, (datetime.now().isoformat(), agent_id))
        self.conn.commit()

    def increment_agent_matches(self, agent_id: str):
        """Increment the matches_found counter"""
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE active_agents
        SET matches_found = matches_found + 1
        WHERE agent_id = ?
        """, (agent_id,))
        self.conn.commit()

    # ===== MATCH OPERATIONS =====

    def add_match(self, agent_id: str, property_address: str, property_data: Dict) -> str:
        """Add a new property match for an agent"""
        match_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO agent_matches (
            match_id, agent_id, property_address, property_data,
            matched_at, status
        ) VALUES (?, ?, ?, ?, ?, 'new')
        """, (match_id, agent_id, property_address, json.dumps(property_data), now))

        self.conn.commit()
        self.increment_agent_matches(agent_id)

        return match_id

    def get_agent_matches(self, agent_id: str, status: Optional[str] = None) -> List[Dict]:
        """Get all matches for an agent"""
        cursor = self.conn.cursor()

        if status:
            cursor.execute("""
            SELECT * FROM agent_matches
            WHERE agent_id = ? AND status = ?
            ORDER BY matched_at DESC
            """, (agent_id, status))
        else:
            cursor.execute("""
            SELECT * FROM agent_matches
            WHERE agent_id = ?
            ORDER BY matched_at DESC
            """, (agent_id,))

        matches = []
        for row in cursor.fetchall():
            match = dict(row)
            if match.get('property_data'):
                match['property_data'] = json.loads(match['property_data'])
            matches.append(match)

        return matches

    def mark_match_notified(self, match_id: str):
        """Mark a match as notified"""
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE agent_matches
        SET notified = 1, notified_at = ?
        WHERE match_id = ?
        """, (datetime.now().isoformat(), match_id))
        self.conn.commit()

    def update_match_status(self, match_id: str, status: str):
        """Update match status (new, sent, viewed, contacted, closed)"""
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE agent_matches SET status = ? WHERE match_id = ?
        """, (status, match_id))
        self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Singleton instance
_db_instance = None

def get_db() -> ClientDatabase:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ClientDatabase()
    return _db_instance
