#!/usr/bin/env python3
"""Enhanced Memory System with Vector Database"""

import json
import sqlite3
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.ultron_logger import log_info, log_error
from pathlib import Path

class EnhancedMemorySystem:
    def __init__(self, db_path="memory/ultron_memory.db"):
        # Ensure path is a string and handle it properly
        if db_path == ":memory:":
            self.db_path = ":memory:"
        else:
            self.db_path = str(db_path)
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for memory storage"""
        try:
            if self.db_path != ":memory:":
                import os
                db_dir = os.path.dirname(self.db_path)
                if db_dir:  # Only create if there's a directory component
                    os.makedirs(db_dir, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    user_input TEXT,
                    agent_response TEXT,
                    context TEXT,
                    embedding BLOB
                )
            ''')
            
            # Knowledge base table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INTEGER PRIMARY KEY,
                    topic TEXT,
                    content TEXT,
                    source TEXT,
                    timestamp TEXT,
                    embedding BLOB
                )
            ''')
            
            conn.commit()
            conn.close()
            log_info("memory_system", "Enhanced memory database initialized")
        except Exception as e:
            log_error("memory_system", f"Database initialization failed: {e}")
    
    def store_conversation(self, user_input: str, agent_response: str, context: Dict = None):
        """Store conversation with vector embedding"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            context_json = json.dumps(context or {})
            
            # Simple embedding (in production, use sentence-transformers)
            embedding = self._create_simple_embedding(user_input + " " + agent_response)
            
            cursor.execute('''
                INSERT INTO conversations (timestamp, user_input, agent_response, context, embedding)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, user_input, agent_response, context_json, embedding.tobytes()))
            
            conn.commit()
            conn.close()
            log_info("memory_system", f"Conversation stored: {user_input[:50]}...")
        except Exception as e:
            log_error("memory_system", f"Failed to store conversation: {e}")
    
    def retrieve_similar_conversations(self, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve similar conversations using vector similarity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query_embedding = self._create_simple_embedding(query)
            
            cursor.execute('SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 100')
            conversations = cursor.fetchall()
            
            similarities = []
            for conv in conversations:
                stored_embedding = np.frombuffer(conv[5], dtype=np.float32)
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                similarities.append((similarity, conv))
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for similarity, conv in similarities[:limit]:
                results.append({
                    'similarity': similarity,
                    'timestamp': conv[1],
                    'user_input': conv[2],
                    'agent_response': conv[3],
                    'context': json.loads(conv[4])
                })
            
            conn.close()
            return results
        except Exception as e:
            log_error("memory_system", f"Failed to retrieve conversations: {e}")
            return []
    
    def _create_simple_embedding(self, text: str) -> np.ndarray:
        """Create simple embedding (replace with proper model in production)"""
        # Simple hash-based embedding for demonstration
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32)
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def get_conversation_summary(self, days: int = 7) -> str:
        """Get conversation summary for the last N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT user_input, agent_response FROM conversations 
                WHERE timestamp > ? ORDER BY timestamp DESC LIMIT 50
            ''', (cutoff_date,))
            
            conversations = cursor.fetchall()
            conn.close()
            
            if not conversations:
                return "No recent conversations found."
            
            # Simple summarization
            topics = set()
            for user_input, _ in conversations:
                words = user_input.lower().split()
                topics.update([w for w in words if len(w) > 4])
            
            return f"Recent topics discussed: {', '.join(list(topics)[:10])}"
        except Exception as e:
            log_error("memory_system", f"Failed to generate summary: {e}")
            return "Summary generation failed."