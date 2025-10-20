"""
PostgreSQL/Supabase Database Integration Tool for ULTRON Agent
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from utils.ultron_logger import log_info, log_error
from .tool_interface import ToolInterface

class DatabaseIntegrationTool(ToolInterface):
    """Tool for PostgreSQL/Supabase database operations"""
    
    @property
    def name(self) -> str:
        return "Database Integration Tool"
    @property
    def description(self) -> str:
        return "PostgreSQL/Supabase database operations and queries"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.connection = None
        # Get connection details from environment or config
        self.connection_string = os.getenv(
            "POSTGRES_URL", 
            "postgresql://postgres:%25RS%40havikz11@localhost:5432/postgres"
        )
    
    def connect(self):
        """Establish database connection"""
        try:
            # Try connection string first
            self.connection = psycopg2.connect(self.connection_string)
            log_info("database", "Connected to PostgreSQL database")
            return True
        except Exception as e:
            log_error("database", f"Connection failed: {e}")
            # Try local fallback
            try:
                self.connection = psycopg2.connect(
                    host="localhost",
                    port=5432,
                    database="postgres",
                    user="postgres",
                    password="postgres"
                )
                log_info("database", "Connected to local PostgreSQL")
                return True
            except Exception as e2:
                log_error("database", f"Local connection also failed: {e2}")
                return False
    
    def match(self, command: str) -> bool:
        """Check if command matches database operations"""
        return any(keyword in command.lower() for keyword in [
            "database", "db", "sql", "query", "postgres", "supabase"
        ])
    
    def execute(self, command: str) -> str:
        """Execute database operations"""
        if not self.connection and not self.connect():
            return "Database connection failed"
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if "create table" in command.lower():
                    return self._create_table(cursor, command)
                elif "select" in command.lower():
                    return self._execute_query(cursor, command)
                elif "insert" in command.lower():
                    return self._execute_insert(cursor, command)
                elif "show tables" in command.lower():
                    return self._show_tables(cursor)
                else:
                    return self._execute_raw_sql(cursor, command)
        except Exception as e:
            log_error("database", f"Query execution failed: {e}")
            return f"Database error: {str(e)}"
    
    def _execute_query(self, cursor, query):
        """Execute SELECT query"""
        cursor.execute(query)
        results = cursor.fetchall()
        return f"Query results: {len(results)} rows\n{results}"
    
    def _execute_insert(self, cursor, query):
        """Execute INSERT query"""
        cursor.execute(query)
        self.connection.commit()
        return f"Insert successful: {cursor.rowcount} rows affected"
    
    def _show_tables(self, cursor):
        """Show all tables"""
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        return f"Tables: {[t['table_name'] for t in tables]}"
    
    def _create_table(self, cursor, query):
        """Create table"""
        cursor.execute(query)
        self.connection.commit()
        return "Table created successfully"
    
    def _execute_raw_sql(self, cursor, query):
        """Execute raw SQL"""
        cursor.execute(query)
        if cursor.description:
            results = cursor.fetchall()
            return f"Results: {results}"
        else:
            self.connection.commit()
            return f"Query executed: {cursor.rowcount} rows affected"
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            log_info("database", "Database connection closed")
    
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
                        "description": "SQL command or database operation"
                    }
                },
                "required": ["command"]
            }
        }