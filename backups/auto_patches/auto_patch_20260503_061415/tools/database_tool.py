"""
Database Integration Tool for ULTRON Agent

Provides database connectivity and persistent storage capabilities
"""

import logging
import os
import sqlite3
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    # log_error will be called after imports

try:
    import pymongo
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    # log_error will be called after imports

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision


class DatabaseTool:
    """
    Tool for database operations and persistent storage
    """

    name = "Database Integration Tool"
    description = "Connect to databases, store/retrieve data, and manage persistent storage"

    def __init__(self):
        self.db_type = os.environ.get('ULTRON_DB_TYPE', 'sqlite')  # sqlite, postgresql, mongodb
        self.connection = None
        self.db_path = Path("data/ultron_data.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Log availability of database drivers
        if not POSTGRESQL_AVAILABLE:
            log_error("database_tool", "PostgreSQL support not available. Install with: pip install psycopg2-binary")
        if not MONGODB_AVAILABLE:
            log_error("database_tool", "MongoDB support not available. Install with: pip install pymongo")

        # Initialize database
        self._initialize_database()

    def match(self, command: str) -> bool:
        """Check if command matches database operations"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "database", "store data", "retrieve data", "save to db", "query database",
            "persistent storage", "data persistence", "db connect", "sql query"
        ])

    def execute(self, command: str) -> str:
        """Execute database operations"""
        try:
            command_lower = command.lower()

            if "store data" in command_lower or "save to db" in command_lower:
                data = self._extract_data(command)
                table = self._extract_table(command)
                if data and table:
                    return self.store_data(table, data)
                else:
                    return "Please specify table name and data to store"
            elif "retrieve data" in command_lower or "query database" in command_lower:
                query = self._extract_query(command)
                if query:
                    return self.query_data(query)
                else:
                    return "Please provide a query to execute"
            elif "create table" in command_lower:
                table_def = self._extract_table_definition(command)
                if table_def:
                    return self.create_table(table_def)
                else:
                    return "Please provide table definition"
            elif "database status" in command_lower:
                return self.get_database_status()
            else:
                return self.get_help()

        except Exception as e:
            log_error("database_tool", f"Database operation failed: {e}")
            return f"Database operation failed: {str(e)}"

    def _initialize_database(self):
        """Initialize the database connection and schema"""
        try:
            if self.db_type == 'sqlite':
                self.connection = sqlite3.connect(str(self.db_path))
                self.connection.row_factory = sqlite3.Row
                self._create_default_tables()
            elif self.db_type == 'postgresql':
                # PostgreSQL connection would go here
                pass
            log_info("database_tool", f"Database initialized: {self.db_type}")
        except Exception as e:
            log_error("database_tool", f"Database initialization failed: {e}")

    def _get_table_columns(self, table: str) -> List[str]:
        """Get valid columns for a table - used for input validation"""
        table_columns = {
            'conversations': ['id', 'timestamp', 'user_input', 'ai_response', 'context', 'metadata'],
            'memory_items': ['id', 'timestamp', 'key', 'value', 'category', 'importance', 'expires_at'],
            'tasks': ['id', 'timestamp', 'title', 'description', 'status', 'priority', 'due_date', 'metadata'],
            'analytics': ['id', 'timestamp', 'event_type', 'event_data', 'session_id', 'user_id']
        }
        return table_columns.get(table, [])

    def _create_default_tables(self):
        """Create default tables for ULTRON data storage"""
        try:
            cursor = self.connection.cursor()

            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_input TEXT,
                    ai_response TEXT,
                    context TEXT,
                    metadata TEXT
                )
            ''')

            # Memory items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    key TEXT UNIQUE,
                    value TEXT,
                    category TEXT,
                    importance REAL DEFAULT 0.5,
                    expires_at TEXT
                )
            ''')

            # Tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority TEXT DEFAULT 'medium',
                    due_date TEXT,
                    metadata TEXT
                )
            ''')

            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT,
                    event_data TEXT,
                    session_id TEXT,
                    user_id TEXT
                )
            ''')

            self.connection.commit()
            log_info("database_tool", "Default tables created")

        except Exception as e:
            log_error("database_tool", f"Table creation failed: {e}")

    def store_data(self, table: str, data: Dict[str, Any]) -> str:
        """Store data in the specified table with SQL injection protection"""
        try:
            # ⚠️ SECURITY: Validate table name to prevent SQL injection
            allowed_tables = {'conversations', 'memory_items', 'tasks', 'analytics'}
            if table not in allowed_tables:
                log_error("database_tool", f"Invalid table name: {table}")
                return f"❌ Invalid table name: '{table}'. Allowed: {allowed_tables}"

            cursor = self.connection.cursor()

            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()

            # ⚠️ SECURITY: Sanitize column names to prevent SQL injection
            valid_columns = set(self._get_table_columns(table))
            sanitized_data = {k: v for k, v in data.items() if k in valid_columns}

            if not sanitized_data:
                return "❌ No valid columns provided"

            columns = ', '.join(sanitized_data.keys())
            placeholders = ', '.join(['?' for _ in sanitized_data])
            values = list(sanitized_data.values())

            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            cursor.execute(query, values)
            self.connection.commit()

            log_info("database_tool", f"Data stored in {table}, ID: {cursor.lastrowid}")
            return f"✅ Data stored successfully in table '{table}' (ID: {cursor.lastrowid})"

        except Exception as e:
            log_error("database_tool", f"Data storage failed: {e}")
            return f"Data storage failed: {str(e)}"

    def query_data(self, query: str) -> str:
        """Execute a SELECT query and return results - WITH SQL INJECTION PROTECTION"""
        try:
            cursor = self.connection.cursor()

            # ⚠️ SECURITY: Only allow SELECT queries - STRICT VALIDATION
            query_upper = query.strip().upper()
            if not query_upper.startswith('SELECT'):
                log_error("database_tool", f"Rejected non-SELECT query: {query[:50]}")
                return "❌ Only SELECT queries are allowed for security reasons"

            # ⚠️ SECURITY: Prevent dangerous SQL keywords in SELECT queries
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'EXEC', 'EXECUTE']
            for keyword in dangerous_keywords:
                if f' {keyword} ' in f' {query_upper} ':
                    log_error("database_tool", f"Rejected query with dangerous keyword: {keyword}")
                    return f"❌ Query contains forbidden keyword: {keyword}"

            # Execute the query safely
            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                return "ℹ️ No data found matching the query"

            # Convert to list of dicts
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))

            # Format results
            result_text = f"📊 **Query Results** ({len(results)} rows)\n\n"

            if len(results) <= 10:  # Show all if 10 or fewer
                for i, row in enumerate(results, 1):
                    result_text += f"**Row {i}:**\n"
                    for key, value in row.items():
                        result_text += f"• {key}: {value}\n"
                    result_text += "\n"
            else:  # Show summary for large result sets
                result_text += f"**First 5 rows:**\n"
                for i, row in enumerate(results[:5], 1):
                    result_text += f"**Row {i}:** {str(row)[:100]}...\n"

                result_text += f"\n**... and {len(results) - 5} more rows**\n"

            log_info("database_tool", f"Query executed successfully: {len(results)} rows")
            return result_text

        except Exception as e:
            log_error("database_tool", f"Query execution failed: {e}")
            return f"❌ Query execution failed: {str(e)}"

    def create_table(self, table_definition: str) -> str:
        """Create a new table"""
        try:
            cursor = self.connection.cursor()

            # Basic safety check
            if 'DROP' in table_definition.upper() or 'DELETE' in table_definition.upper():
                return "Table creation cannot include DROP or DELETE statements"

            cursor.execute(table_definition)
            self.connection.commit()

            log_info("database_tool", f"Table created: {table_definition}")
            return "✅ Table created successfully"

        except Exception as e:
            log_error("database_tool", f"Table creation failed: {e}")
            return f"Table creation failed: {str(e)}"

    def get_database_status(self) -> str:
        """Get database status and statistics"""
        try:
            cursor = self.connection.cursor()

            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            status = f"""
🗄️ **Database Status**

**Database Type:** {self.db_type}
**Database Path:** {self.db_path}

**Tables:**
"""

            for table in tables:
                table_name = table[0]

                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]

                # Get columns
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                status += f"• **{table_name}**: {count} rows, {len(columns)} columns\n"

                # Show column info for first few tables
                if len(tables) <= 5:
                    for col in columns:
                        status += f"  - {col[1]} ({col[2]})\n"

            # Database file size
            if self.db_path.exists():
                size = self.db_path.stat().st_size
                status += f"\n**Database Size:** {size:,} bytes ({size/1024/1024:.2f} MB)"

            return status

        except Exception as e:
            log_error("database_tool", f"Status check failed: {e}")
            return f"Status check failed: {str(e)}"

    def _extract_data(self, command: str) -> Optional[Dict[str, Any]]:
        """Extract data from command (simple JSON-like parsing)"""
        # Look for JSON-like data in the command
        import re
        json_match = re.search(r'\{.*\}', command, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Simple key-value extraction
        data = {}
        pairs = re.findall(r'(\w+):\s*([^,\n]+)', command)
        for key, value in pairs:
            data[key.strip()] = value.strip()

        return data if data else None

    def _extract_table(self, command: str) -> Optional[str]:
        """Extract table name from command"""
        import re
        # Look for table name patterns
        match = re.search(r'table\s+(\w+)', command, re.IGNORECASE)
        if match:
            return match.group(1)

        # Look for common table names
        tables = ['conversations', 'memory_items', 'tasks', 'analytics']
        for table in tables:
            if table in command.lower():
                return table

        return None

    def _extract_query(self, command: str) -> Optional[str]:
        """Extract SQL query from command"""
        # Look for SELECT statement
        select_match = re.search(r'select\s+.*?(?:from\s+\w+.*?)(?:where\s+.*?)?(?:limit\s+\d+)?', command, re.IGNORECASE | re.DOTALL)
        if select_match:
            return select_match.group(0).strip()

        # If no explicit SELECT, try to construct one
        if 'from' in command.lower():
            return command.strip()

        return None

    def _extract_table_definition(self, command: str) -> Optional[str]:
        """Extract CREATE TABLE statement"""
        import re
        create_match = re.search(r'create\s+table\s+.*?(?:\([^)]+\))', command, re.IGNORECASE | re.DOTALL)
        if create_match:
            return create_match.group(0).strip()

        return None

    def get_help(self) -> str:
        """Get help information for the tool"""
        return """
🗄️ **Database Integration Tool**

**Capabilities:**
• Persistent data storage and retrieval
• SQL query execution (SELECT only for security)
• Table creation and management
• Database status monitoring
• Multiple database support (SQLite, PostgreSQL planned)

**Commands:**
• "store data table conversations {user_input: 'hello', ai_response: 'hi'}" - Store data
• "retrieve data SELECT * FROM conversations LIMIT 5" - Query data
• "create table CREATE TABLE test (id INTEGER, name TEXT)" - Create table
• "database status" - Check database status

**Default Tables:**
• conversations - Chat history
• memory_items - Persistent memory
• tasks - Task management
• analytics - Usage analytics

**Features:**
• Automatic timestamping
• Data validation
• Query safety checks
• SQLite backend with PostgreSQL support planned
"""

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Database operation command"
                    }
                },
                "required": ["command"]
            }
        }
