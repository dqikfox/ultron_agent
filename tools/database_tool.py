from .base import Tool
import logging
from supabase import create_client

class DatabaseTool(Tool):
    def __init__(self, config):
        self.name = "DatabaseTool"
        self.description = "Query or update Supabase PostgreSQL database."
        self.config = config
        self.supabase = None
        if config.data.get("supabase_url") and config.data.get("supabase_anon_key"):
            self.supabase = create_client(config.data["supabase_url"], config.data["supabase_anon_key"])
        super().__init__()

    def match(self, command: str) -> bool:
        cmd = command.lower()
        return "database" in cmd or "query" in cmd or "update" in cmd

    def execute(self, command: str) -> str:
        if not self.supabase:
            return "Supabase not configured."
        try:
            parts = command.split()
            if "query" in command.lower():
                table = parts[parts.index("from") + 1] if "from" in parts else "default_table"
                response = self.supabase.table(table).select("*").execute()
                return str(response.data)
            elif "update" in command.lower():
                table = parts[parts.index("table") + 1] if "table" in parts else "default_table"
                data = {"updated_at": "now()"}  # Example update
                response = self.supabase.table(table).insert(data).execute()
                return "Update successful."
            return "Unknown database command."
        except Exception as e:
            logging.error(f"Database error: {e}")
            return f"Error: {e}"