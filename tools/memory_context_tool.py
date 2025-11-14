"""
ULTRON Agent - Memory Context Tool
Contextual memory for natural language understanding and conversation history.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from utils.ultron_logger import log_info, log_error


class MemoryContextTool:
    """Contextual memory system for natural language understanding"""
    
    name = "memory_context"
    description = "Contextual memory for conversation history and user preferences"
    
    def __init__(self):
        self.db_path = Path("memory/context.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for memory storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_input TEXT NOT NULL,
                        system_response TEXT NOT NULL,
                        context_tags TEXT,
                        session_id TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT NOT NULL,
                        results TEXT,
                        timestamp TEXT NOT NULL,
                        source TEXT
                    )
                """)
                
                log_info("memory_context", "Memory database initialized")
                
        except Exception as e:
            log_error("memory_context", f"Database init failed: {str(e)}")
    
    def match(self, command: str) -> bool:
        """Match memory-related commands"""
        keywords = ["remember", "recall", "history", "yesterday", "last", "recent", "context"]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute memory operations"""
        try:
            cmd_lower = command.lower()
            
            if "remember" in cmd_lower:
                return self._store_memory(command, kwargs)
            elif any(word in cmd_lower for word in ["recall", "yesterday", "recent", "last"]):
                return self._recall_memory(command)
            elif "history" in cmd_lower:
                return self._get_history(command)
            elif "search" in cmd_lower and any(word in cmd_lower for word in ["yesterday", "recent"]):
                return self._recall_search_history(command)
            else:
                return self._general_context_query(command)
                
        except Exception as e:
            log_error("memory_context", f"Memory operation failed: {str(e)}")
            return f"Memory error: {str(e)}"
    
    def _store_memory(self, command: str, context: Dict) -> str:
        """Store conversation or context in memory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                timestamp = datetime.now().isoformat()
                
                # Extract what to remember
                user_input = context.get("user_input", command)
                system_response = context.get("system_response", "")
                tags = self._extract_context_tags(command)
                session_id = context.get("session_id", "default")
                
                conn.execute("""
                    INSERT INTO conversations 
                    (timestamp, user_input, system_response, context_tags, session_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (timestamp, user_input, system_response, json.dumps(tags), session_id))
                
                log_info("memory_context", f"Stored memory: {tags}")
                return f"Remembered: {', '.join(tags)}"
                
        except Exception as e:
            log_error("memory_context", f"Store memory failed: {str(e)}")
            return f"Failed to store memory: {str(e)}"
    
    def _recall_memory(self, command: str) -> str:
        """Recall relevant memories based on query"""
        try:
            # Parse temporal references
            timeframe = self._parse_timeframe(command)
            keywords = self._extract_search_keywords(command)
            
            with sqlite3.connect(self.db_path) as conn:
                # Build query based on timeframe and keywords
                query = """
                    SELECT timestamp, user_input, system_response, context_tags
                    FROM conversations
                    WHERE timestamp > ?
                """
                params = [timeframe]
                
                if keywords:
                    keyword_conditions = []
                    for keyword in keywords:
                        keyword_conditions.append("(user_input LIKE ? OR context_tags LIKE ?)")
                        params.extend([f"%{keyword}%", f"%{keyword}%"])
                    
                    query += " AND (" + " OR ".join(keyword_conditions) + ")"
                
                query += " ORDER BY timestamp DESC LIMIT 10"
                
                cursor = conn.execute(query, params)
                results = cursor.fetchall()
                
                if results:
                    memories = []
                    for row in results:
                        timestamp, user_input, system_response, context_tags = row
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime("%Y-%m-%d %H:%M")
                        
                        tags = json.loads(context_tags) if context_tags else []
                        memories.append(f"[{time_str}] {user_input} (Tags: {', '.join(tags)})")
                    
                    return f"Found {len(memories)} relevant memories:\n" + "\n".join(memories)
                else:
                    return "No relevant memories found for that timeframe"
                    
        except Exception as e:
            log_error("memory_context", f"Recall memory failed: {str(e)}")
            return f"Failed to recall memories: {str(e)}"
    
    def _get_history(self, command: str) -> str:
        """Get conversation history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, user_input, system_response
                    FROM conversations
                    ORDER BY timestamp DESC
                    LIMIT 20
                """)
                
                results = cursor.fetchall()
                
                if results:
                    history = []
                    for row in results:
                        timestamp, user_input, system_response = row
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime("%H:%M")
                        history.append(f"[{time_str}] User: {user_input}")
                        if system_response:
                            history.append(f"[{time_str}] System: {system_response}")
                    
                    return "Recent conversation history:\n" + "\n".join(history[-10:])
                else:
                    return "No conversation history found"
                    
        except Exception as e:
            return f"History retrieval failed: {str(e)}"
    
    def _recall_search_history(self, command: str) -> str:
        """Recall previous search queries"""
        try:
            keywords = self._extract_search_keywords(command)
            timeframe = self._parse_timeframe(command)
            
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT query, timestamp, source
                    FROM search_history
                    WHERE timestamp > ?
                """
                params = [timeframe]
                
                if keywords:
                    keyword_conditions = []
                    for keyword in keywords:
                        keyword_conditions.append("query LIKE ?")
                        params.append(f"%{keyword}%")
                    
                    query += " AND (" + " OR ".join(keyword_conditions) + ")"
                
                query += " ORDER BY timestamp DESC LIMIT 5"
                
                cursor = conn.execute(query, params)
                results = cursor.fetchall()
                
                if results:
                    searches = []
                    for row in results:
                        query_text, timestamp, source = row
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime("%Y-%m-%d %H:%M")
                        searches.append(f"[{time_str}] {source}: {query_text}")
                    
                    return f"Found recent searches:\n" + "\n".join(searches)
                else:
                    return "No matching search history found"
                    
        except Exception as e:
            return f"Search history recall failed: {str(e)}"
    
    def _general_context_query(self, command: str) -> str:
        """Handle general context queries"""
        # For commands like "the car thing we looked at yesterday"
        if "car" in command.lower() and any(word in command.lower() for word in ["yesterday", "recent", "looked"]):
            return self._recall_car_related_context()
        
        return "Context query processed - no specific matches found"
    
    def _recall_car_related_context(self) -> str:
        """Specific handler for car-related queries"""
        try:
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Check conversations for car mentions
                cursor = conn.execute("""
                    SELECT user_input, timestamp
                    FROM conversations
                    WHERE (user_input LIKE '%car%' OR context_tags LIKE '%car%')
                    AND timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT 3
                """, (yesterday,))
                
                conversations = cursor.fetchall()
                
                # Check search history for car searches
                cursor = conn.execute("""
                    SELECT query, timestamp, source
                    FROM search_history
                    WHERE query LIKE '%car%'
                    AND timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT 3
                """, (yesterday,))
                
                searches = cursor.fetchall()
                
                results = []
                
                if conversations:
                    results.append("Recent car-related conversations:")
                    for user_input, timestamp in conversations:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime("%H:%M")
                        results.append(f"  [{time_str}] {user_input}")
                
                if searches:
                    results.append("Recent car-related searches:")
                    for query, timestamp, source in searches:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime("%H:%M")
                        results.append(f"  [{time_str}] {source}: {query}")
                
                if results:
                    return "\n".join(results)
                else:
                    return "No recent car-related activity found. Would you like me to search for cars now?"
                    
        except Exception as e:
            return f"Car context recall failed: {str(e)}"
    
    def store_search_query(self, query: str, source: str = "browser", results: str = "") -> None:
        """Store search query for future reference"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                timestamp = datetime.now().isoformat()
                conn.execute("""
                    INSERT INTO search_history (query, results, timestamp, source)
                    VALUES (?, ?, ?, ?)
                """, (query, results, timestamp, source))
                
                log_info("memory_context", f"Stored search: {query}")
                
        except Exception as e:
            log_error("memory_context", f"Store search failed: {str(e)}")
    
    def _extract_context_tags(self, text: str) -> List[str]:
        """Extract context tags from text"""
        tags = []
        words = text.lower().split()
        
        # Common entities and topics
        entities = ["car", "house", "job", "project", "meeting", "file", "document", "email"]
        actions = ["search", "open", "close", "create", "delete", "edit", "view"]
        
        for word in words:
            if word in entities:
                tags.append(word)
            elif word in actions:
                tags.append(word)
        
        return list(set(tags))  # Remove duplicates
    
    def _extract_search_keywords(self, command: str) -> List[str]:
        """Extract search keywords from command"""
        # Remove common words
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = [w.lower() for w in command.split() if w.lower() not in stop_words and len(w) > 2]
        
        # Remove command words
        command_words = {"recall", "remember", "history", "yesterday", "recent", "last", "search", "find"}
        keywords = [w for w in words if w not in command_words]
        
        return keywords[:5]  # Limit to 5 keywords
    
    def _parse_timeframe(self, command: str) -> str:
        """Parse temporal references in command"""
        now = datetime.now()
        
        if "yesterday" in command.lower():
            return (now - timedelta(days=1)).isoformat()
        elif "last week" in command.lower():
            return (now - timedelta(weeks=1)).isoformat()
        elif "recent" in command.lower() or "last" in command.lower():
            return (now - timedelta(hours=24)).isoformat()
        else:
            return (now - timedelta(days=7)).isoformat()  # Default to last week
    
    @staticmethod
    def schema():
        return {
            "name": "memory_context",
            "description": "Contextual memory for conversation history and user preferences",
            "parameters": {
                "command": {"type": "string", "description": "Memory command"},
                "user_input": {"type": "string", "description": "User input to remember"},
                "system_response": {"type": "string", "description": "System response"},
                "session_id": {"type": "string", "description": "Session identifier"}
            }
        }