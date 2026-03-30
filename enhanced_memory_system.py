#!/usr/bin/env python3
"""Enhanced Memory System with Vector Database and Transformer-Based Embeddings

Phase B Enhancement: Semantic memory with sentence-transformers for superior
semantic similarity matching and clustering.
"""

import json
import sqlite3
import threading
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from utils.ultron_logger import log_info, log_error
from pathlib import Path

# ✨ PHASE B: Use transformer-based embeddings for semantic understanding
try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    log_error("memory_system", "sentence-transformers not installed, falling back to hash-based embeddings")

class EnhancedMemorySystem:
    def __init__(self, db_path="memory/ultron_memory.db", model_name: str = 'all-MiniLM-L6-v2'):
        # Ensure path is a string and handle it properly
        if db_path == ":memory:":
            self.db_path = ":memory:"
        else:
            self.db_path = str(db_path)

        # ✨ PHASE B: Initialize transformer model for embeddings
        self.transformer_model = None
        self.embedding_dim = None
        # Track availability as an instance attribute to avoid module-level mutation
        self._transformers_available = TRANSFORMERS_AVAILABLE

        if self._transformers_available:
            try:
                log_info("memory_system", f"Loading transformer model: {model_name}")
                self.transformer_model = SentenceTransformer(model_name)
                # all-MiniLM-L6-v2 produces 384-dimensional embeddings
                self.embedding_dim = self.transformer_model.get_sentence_embedding_dimension()
                log_info("memory_system", f"Transformer model loaded, embedding dimension: {self.embedding_dim}")
            except Exception as e:
                log_error("memory_system", f"Failed to load transformer model: {e}, falling back to hash-based")
                self._transformers_available = False

        # Per-thread SQLite connection cache to avoid repeated connect/close overhead
        self._local = threading.local()

        # Small LRU-style embedding cache: maps text → (embedding_array, model_name)
        self._embedding_cache: Dict[str, Tuple[np.ndarray, str]] = {}
        self._embedding_cache_max = 256

        self.init_database()

    # ------------------------------------------------------------------
    # Database connection helpers
    # ------------------------------------------------------------------

    def _get_connection(self) -> sqlite3.Connection:
        """Return a per-thread SQLite connection, creating it if needed.

        Using a per-thread connection avoids the overhead of opening and
        closing a new connection for every database operation while
        remaining safe for multi-threaded use.
        """
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn = conn
        return conn
        
    def init_database(self):
        """Initialize SQLite database for memory storage"""
        try:
            if self.db_path != ":memory:":
                import os
                db_dir = os.path.dirname(self.db_path)
                if db_dir:  # Only create if there's a directory component
                    os.makedirs(db_dir, exist_ok=True)

            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    user_input TEXT,
                    agent_response TEXT,
                    context TEXT,
                    embedding BLOB,
                    embedding_model TEXT
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
                    embedding BLOB,
                    embedding_model TEXT
                )
            ''')
            
            # ✨ PHASE B: Semantic clusters table for memory organization
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS semantic_clusters (
                    id INTEGER PRIMARY KEY,
                    cluster_id INTEGER,
                    conversation_id INTEGER,
                    timestamp TEXT
                )
            ''')
            
            conn.commit()
            log_info("memory_system", "Enhanced memory database initialized")
        except Exception as e:
            log_error("memory_system", f"Database initialization failed: {e}")

    def store_conversation(self, user_input: str, agent_response: str, metadata: Dict = None, context: Dict = None):
        """Store conversation with transformer-based embedding"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            timestamp = datetime.now().isoformat()
            context_json = json.dumps(context or {})

            # ✨ PHASE B: Use transformer embedding if available
            embedding, model_name = self._create_embedding(user_input + " " + agent_response)

            cursor.execute('''
                INSERT INTO conversations (timestamp, user_input, agent_response, context, embedding, embedding_model)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, user_input, agent_response, context_json, embedding.tobytes(), model_name))

            conn.commit()
            log_info("memory_system", f"Conversation stored ({model_name}): {user_input[:50]}...")
        except Exception as e:
            log_error("memory_system", f"Failed to store conversation: {e}")


    def retrieve_similar_conversations(self, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve similar conversations using transformer-based vector similarity"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # ✨ PHASE B: Use transformer embedding for query (cached to avoid re-encoding)
            query_embedding, model_used = self._create_embedding(query)

            cursor.execute('SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 100')
            conversations = cursor.fetchall()

            if not conversations:
                return []

            # Vectorised batch cosine similarity – faster than a Python loop
            stored_embeddings = np.array(
                [np.frombuffer(conv[5], dtype=np.float32) for conv in conversations]
            )
            # query_embedding shape: (D,), stored shape: (N, D)
            dot_products = stored_embeddings.dot(query_embedding)
            norms = np.linalg.norm(stored_embeddings, axis=1) * np.linalg.norm(query_embedding)
            # Avoid division by zero for zero-norm embeddings
            similarities = np.where(norms > 0, dot_products / norms, 0.0)

            # Partial sort – only need top `limit` results
            top_indices = np.argpartition(similarities, -min(limit, len(similarities)))[-limit:]
            top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]

            results = []
            for idx in top_indices:
                conv = conversations[idx]
                results.append({
                    'similarity': float(similarities[idx]),
                    'timestamp': conv[1],
                    'user_input': conv[2],
                    'agent_response': conv[3],
                    'context': json.loads(conv[4]),
                    'model': conv[6] if len(conv) > 6 else 'unknown'
                })

            return results
        except Exception as e:
            log_error("memory_system", f"Failed to retrieve conversations: {e}")
            return []

    def _create_embedding(self, text: str) -> Tuple[np.ndarray, str]:
        """Create transformer-based or hash-based embedding, with caching.

        Results are cached in a bounded dict so identical queries (common
        during search loops) avoid redundant encoding work.

        Returns: (embedding_vector, model_name)
        """
        cached = self._embedding_cache.get(text)
        if cached is not None:
            return cached

        # ✨ PHASE B: Try transformer-based embedding first
        if self.transformer_model is not None:
            try:
                embedding = self.transformer_model.encode(text, convert_to_numpy=True).astype(np.float32)
                result: Tuple[np.ndarray, str] = (embedding, "sentence-transformers")
            except Exception as e:
                log_error("memory_system", f"Transformer embedding failed: {e}, falling back to hash-based")
                result = (self._create_simple_embedding(text), "hash-based")
        else:
            # Fallback to hash-based embedding
            result = (self._create_simple_embedding(text), "hash-based")

        # Evict oldest entry when cache is full (simple FIFO eviction)
        if len(self._embedding_cache) >= self._embedding_cache_max:
            try:
                self._embedding_cache.pop(next(iter(self._embedding_cache)))
            except StopIteration:
                pass
        self._embedding_cache[text] = result
        return result
    
    def _create_simple_embedding(self, text: str) -> np.ndarray:
        """Create hash-based embedding (fallback when transformers unavailable)"""
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
    
    # ✨ PHASE B: Semantic Clustering Methods
    def cluster_memories(self, n_clusters: int = 5) -> List[List[Dict]]:
        """Cluster similar memories using semantic embeddings
        
        Returns: List of clusters, where each cluster is a list of memory items
        """
        try:
            from sklearn.cluster import KMeans
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM conversations LIMIT 100')
            conversations = cursor.fetchall()
            conn.close()
            
            if len(conversations) < n_clusters:
                # Not enough conversations to cluster
                return [[{"id": c[0], "text": c[2]} for c in conversations]]
            
            # Extract embeddings
            embeddings = []
            for conv in conversations:
                emb = np.frombuffer(conv[5], dtype=np.float32)
                embeddings.append(emb)
            
            # Cluster embeddings
            embeddings_array = np.array(embeddings)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings_array)
            
            # Group by cluster
            clusters = [[] for _ in range(n_clusters)]
            for idx, label in enumerate(labels):
                conv = conversations[idx]
                clusters[label].append({
                    'id': conv[0],
                    'timestamp': conv[1],
                    'user_input': conv[2][:100],
                    'cluster': label
                })
            
            log_info("memory_system", f"Clustered {len(conversations)} memories into {n_clusters} clusters")
            return clusters
        
        except ImportError:
            log_error("memory_system", "scikit-learn not available for clustering")
            return []
        except Exception as e:
            log_error("memory_system", f"Clustering failed: {e}")
            return []
    
    def get_semantic_stats(self) -> Dict[str, Any]:
        """Get statistics about semantic memory
        
        Returns: Dictionary with memory statistics and model information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM conversations')
            num_conversations = cursor.fetchone()[0]
            
            cursor.execute('SELECT DISTINCT embedding_model FROM conversations')
            models_used = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT MAX(timestamp) FROM conversations')
            latest = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                'total_conversations': num_conversations,
                'embedding_models': models_used,
                'latest_memory': latest,
                'transformer_available': TRANSFORMERS_AVAILABLE,
                'embedding_dimension': self.embedding_dim if self.transformer_model else 16,
                'system_status': 'transformers' if TRANSFORMERS_AVAILABLE else 'hash-based fallback'
            }
            
            return stats
        except Exception as e:
            log_error("memory_system", f"Failed to get stats: {e}")
            return {}