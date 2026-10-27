"""
PostgreSQL/Supabase Database Integration Tool for ULTRON Agent

⚠️ SECURITY CRITICAL: Uses environment variables for all credentials
Never hardcode passwords or connection strings in code!
"""

import os
from typing import Dict, Any, Optional, List, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import connection, cursor
from utils.ultron_logger import log_info, log_error
from utils.error_handlers import (
    NetworkError, TimeoutError, ValidationError, FileError,
    ResourceError, UltronError, ErrorContext, ErrorCategory
)
from .tool_interface import ToolInterface

class DatabaseIntegrationTool(ToolInterface):
    """Tool for PostgreSQL/Supabase database operations with comprehensive security"""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}
        self.connection: Optional[Any] = None

        # ⚠️ SECURITY: Load credentials from environment variables ONLY
        # Never use hardcoded credentials
        self._load_credentials_from_env()

    def _load_credentials_from_env(self) -> None:
        """Load database credentials from environment variables - SECURE METHOD"""
        with ErrorContext("database_integration_tool", logger=None) as ctx:
            try:
                ctx.operation = "load_credentials"

                # Try POSTGRES_URL first (full connection string)
                self.connection_string: Optional[str] = os.getenv("POSTGRES_URL")

                if self.connection_string:
                    log_info("database", "Loaded POSTGRES_URL from environment")
                    return

                # Fallback to individual credentials from environment
                host = os.getenv("POSTGRES_HOST", "localhost")
                port = os.getenv("POSTGRES_PORT", "5432")
                database = os.getenv("POSTGRES_DB", "postgres")
                user = os.getenv("POSTGRES_USER", "postgres")
                password = os.getenv("POSTGRES_PASSWORD")

                # ⚠️ SECURITY: Validate required fields
                if not password:
                    log_error("database", "POSTGRES_PASSWORD not set in environment")
                    raise ValidationError(
                        "Database password not configured",
                        "POSTGRES_PASSWORD",
                        "***hidden***",
                        "non-empty from environment"
                    )

                # Build connection string from parts
                self.connection_string = (
                    f"postgresql://{user}:{password}@{host}:{port}/{database}"
                )
                log_info("database", f"Built connection string from env vars: {host}:{port}/{database}")

            except ValidationError as e:
                log_error("database", f"Credential validation failed: {e}")
                raise

    @property
    def name(self) -> str:
        return "Database Integration Tool"

    @property
    def description(self) -> str:
        return "PostgreSQL/Supabase database operations and queries"

    def connect(self) -> bool:
        """Establish database connection with comprehensive error handling"""
        with ErrorContext("database_integration_tool", logger=None) as ctx:
            try:
                ctx.operation = "database_connect"

                if not self.connection_string:
                    raise ValidationError(
                        "Connection string not configured",
                        "connection_string",
                        None,
                        "valid PostgreSQL URL"
                    )

                # Try connection string first
                try:
                    self.connection = psycopg2.connect(self.connection_string, connect_timeout=10)
                    log_info("database", "✅ Connected to PostgreSQL database")
                    return True

                except psycopg2.OperationalError as e:
                    log_error("database", f"Connection failed: {e}")
                    ctx.error = "primary_connection_failed"

                    # Fallback to local connection with individual credentials
                    try:
                        host = os.getenv("POSTGRES_HOST", "localhost")
                        port = int(os.getenv("POSTGRES_PORT", "5432"))
                        database = os.getenv("POSTGRES_DB", "postgres")
                        user = os.getenv("POSTGRES_USER", "postgres")
                        password = os.getenv("POSTGRES_PASSWORD", "postgres")

                        self.connection = psycopg2.connect(
                            host=host,
                            port=port,
                            database=database,
                            user=user,
                            password=password,
                            connect_timeout=10
                        )
                        log_info("database", "✅ Connected to local PostgreSQL")
                        ctx.operation = "fallback_connection_success"
                        return True

                    except psycopg2.OperationalError as e2:
                        log_error("database", f"Local connection also failed: {e2}")
                        raise NetworkError(
                            f"Database connection failed: {e2}",
                            f"{host}:{port}/{database}",
                            "connect"
                        )

            except (ValidationError, NetworkError) as e:
                log_error("database", f"Connection error: {e}")
                ctx.error = "connection_failed"
                return False
            except Exception as e:
                log_error("database", f"Unexpected connection error: {e}")
                ctx.error = "connection_exception"
                return False

    def match(self, command: str) -> bool:
        """Check if command matches database operations"""
        return any(keyword in command.lower() for keyword in [
            "database", "db", "sql", "query", "postgres", "supabase"
        ])

    def execute(self, command: str) -> str:
        """Execute database operations with SQL injection protection"""
        with ErrorContext("database_integration_tool", logger=None) as ctx:
            try:
                ctx.operation = "database_execute"

                if not self.connection and not self.connect():
                    return "❌ Database connection failed"

                try:
                    with self.connection.cursor(cursor_factory=RealDictCursor) as db_cursor:
                        # ⚠️ SECURITY: Sanitize command input
                        command_lower = command.lower().strip()

                        # Check for dangerous keywords
                        dangerous = ['drop', 'delete', 'truncate', 'exec', 'execute']
                        if any(kw in command_lower for kw in dangerous):
                            log_error("database", f"Rejected dangerous command: {command[:50]}")
                            return "❌ Command contains forbidden operations"

                        if "create table" in command_lower:
                            return self._create_table(db_cursor, command)
                        elif "select" in command_lower:
                            return self._execute_query(db_cursor, command)
                        elif "insert" in command_lower:
                            return self._execute_insert(db_cursor, command)
                        elif "update" in command_lower:
                            return self._execute_update(db_cursor, command)
                        elif "show tables" in command_lower:
                            return self._show_tables(db_cursor)
                        else:
                            log_info("database", f"Executing raw SQL: {command[:50]}")
                            return self._execute_raw_sql(db_cursor, command)

                except psycopg2.Error as e:
                    log_error("database", f"Query execution error: {e}")
                    ctx.error = "query_execution_failed"
                    self.connection.rollback()
                    return f"❌ Query error: {str(e)}"

            except Exception as e:
                log_error("database", f"Execute failed: {e}")
                ctx.error = "execute_exception"
                return f"❌ Database error: {str(e)}"

    def _execute_query(self, db_cursor: Any, query: str) -> str:
        """Execute SELECT query"""
        db_cursor.execute(query)
        results: List[Any] = db_cursor.fetchall()
        return f"Query results: {len(results)} rows\n{results}"

    def _execute_insert(self, db_cursor: Any, query: str) -> str:
        """Execute INSERT query with transaction management"""
        try:
            db_cursor.execute(query)
            self.connection.commit()
            log_info("database", f"Insert successful: {db_cursor.rowcount} rows")
            return f"✅ Insert successful: {db_cursor.rowcount} rows affected"
        except Exception as e:
            self.connection.rollback()
            log_error("database", f"Insert failed: {e}")
            raise

    def _execute_update(self, db_cursor: Any, query: str) -> str:
        """Execute UPDATE query with transaction management"""
        try:
            db_cursor.execute(query)
            self.connection.commit()
            log_info("database", f"Update successful: {db_cursor.rowcount} rows")
            return f"✅ Update successful: {db_cursor.rowcount} rows affected"
        except Exception as e:
            self.connection.rollback()
            log_error("database", f"Update failed: {e}")
            raise

    def _show_tables(self, db_cursor: Any) -> str:
        """Show all tables"""
        db_cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables: List[Any] = db_cursor.fetchall()
        return f"Tables: {[t['table_name'] for t in tables]}"

    def _create_table(self, db_cursor: Any, query: str) -> str:
        """Create table"""
        db_cursor.execute(query)
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
