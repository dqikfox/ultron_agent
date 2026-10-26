"""
Memory Manager for UltronSysAgent
Handles short-term and long-term memory storage and retrieval
"""

import asyncio
import logging
import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False
    print("⚠️  Vector database dependencies not available")

from ...core.event_bus import EventBus, EventTypes

class MemoryManager:
    """Manages short-term and long-term memory for UltronSysAgent"""
    
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Memory storage
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "memory"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # SQLite database for structured memory
        self.db_path = self.data_dir / "memory.db"
        self.db_connection = None
        
        # Vector database for semantic search
        self.vector_db = None
        self.embeddings_model = None
        
        # Short-term memory (in-memory storage)
        self.short_term_memory = []
        self.max_short_term = config.get('memory.short_term_limit', 100)
        
        # Cache for frequently accessed memories
        self.memory_cache = {}
        
        # Initialize storage
        self._initialize_storage()
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _initialize_storage(self):
        """Initialize memory storage systems"""
        try:
            # Initialize SQLite database
            self._initialize_sqlite()
            
            # Initialize vector database if available
            if VECTOR_DB_AVAILABLE and self.config.get('memory.vector_db_enabled', True):
                self._initialize_vector_db()
            
            self.logger.info("✅ Memory storage systems initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize memory storage: {e}")
            raise
    
    def _initialize_sqlite(self):
        """Initialize SQLite database for structured memory"""
        self.db_connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.db_connection.row_factory = sqlite3.Row
        
        # Create tables
        cursor = self.db_connection.cursor()
        
        # Conversation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                model_used TEXT,
                session_id TEXT,
                metadata TEXT
            )
        ''')
        
        # Knowledge base table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_hash TEXT UNIQUE,
                source TEXT,
                type TEXT,
                timestamp TEXT NOT NULL,
                tags TEXT,
                metadata TEXT
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Commands history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                result TEXT,
                timestamp TEXT NOT NULL,
                success BOOLEAN,
                admin_mode BOOLEAN
            )
        ''')
        
        self.db_connection.commit()
    
    def _initialize_vector_db(self):
        """Initialize ChromaDB for semantic search"""
        try:
            # Initialize ChromaDB client
            chroma_path = self.data_dir / "chroma"
            self.vector_db = chromadb.PersistentClient(path=str(chroma_path))
            
            # Get or create collection
            self.vector_collection = self.vector_db.get_or_create_collection(
                name="ultron_memory",
                metadata={"description": "UltronSysAgent memory collection"}
            )
            
            # Initialize embeddings model
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            self.logger.info("✅ Vector database initialized")
            
        except Exception as e:
            self.logger.warning(f"Vector database initialization failed: {e}")
            self.vector_db = None
    
    def _setup_event_handlers(self):
        """Setup event bus handlers"""
        self.event_bus.subscribe(EventTypes.MEMORY_STORE, self._handle_memory_store)
        self.event_bus.subscribe(EventTypes.MEMORY_RECALL, self._handle_memory_recall)
        self.event_bus.subscribe(EventTypes.FILE_PROCESSED, self._handle_file_processed)
    
    async def start(self):
        """Start the memory manager"""
        self.logger.info("🧠 Starting Memory Manager...")
        
        # Start auto-save timer
        if self.config.get('memory.auto_save_interval'):
            asyncio.create_task(self._auto_save_loop())
        
        await self.event_bus.publish(EventTypes.MODULE_STARTED, 
                                    {"module": "memory_manager"}, 
                                    source="memory_manager")
    
    async def stop(self):
        """Stop the memory manager"""
        self.logger.info("🧠 Stopping Memory Manager...")
        
        # Save any pending data
        await self._save_short_term_memory()
        
        # Close database connection
        if self.db_connection:
            self.db_connection.close()
        
        await self.event_bus.publish(EventTypes.MODULE_STOPPED, 
                                    {"module": "memory_manager"}, 
                                    source="memory_manager")
    
    async def store_interaction(self, user_input: str, ai_response: str, 
                               model_used: str = None, session_id: str = None):
        """Store a conversation interaction"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Add to short-term memory
            interaction = {
                "timestamp": timestamp,
                "user_input": user_input,
                "ai_response": ai_response,
                "model_used": model_used,
                "session_id": session_id
            }
            
            self.short_term_memory.append(interaction)
            
            # Limit short-term memory size
            if len(self.short_term_memory) > self.max_short_term:
                # Move oldest to long-term storage
                old_interaction = self.short_term_memory.pop(0)
                await self._store_to_long_term(old_interaction)
            
            # Store in vector database for semantic search
            if self.vector_db:
                await self._store_in_vector_db(user_input, ai_response, timestamp)
            
            self.logger.debug(f"Stored interaction: {user_input[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Error storing interaction: {e}")
    
    async def _store_to_long_term(self, interaction: Dict):
        """Store interaction in long-term SQLite database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO conversations 
                (timestamp, user_input, ai_response, model_used, session_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                interaction['timestamp'],
                interaction['user_input'],
                interaction['ai_response'],
                interaction.get('model_used'),
                interaction.get('session_id'),
                json.dumps(interaction.get('metadata', {}))
            ))
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing to long-term memory: {e}")
    
    async def _store_in_vector_db(self, user_input: str, ai_response: str, timestamp: str):
        """Store interaction in vector database for semantic search"""
        try:
            if not self.vector_db or not self.embeddings_model:
                return
            
            # Create combined text for embedding
            combined_text = f"User: {user_input}\nAssistant: {ai_response}"
            
            # Generate embedding
            embedding = self.embeddings_model.encode(combined_text).tolist()
            
            # Store in ChromaDB
            doc_id = hashlib.md5(combined_text.encode()).hexdigest()
            
            self.vector_collection.add(
                documents=[combined_text],
                embeddings=[embedding],
                metadatas=[{
                    "timestamp": timestamp,
                    "user_input": user_input,
                    "ai_response": ai_response
                }],
                ids=[doc_id]
            )
            
        except Exception as e:
            self.logger.error(f"Error storing in vector database: {e}")
    
    async def get_relevant_context(self, query: str, limit: int = 5) -> str:
        """Get relevant context from memory for a query"""
        try:
            contexts = []
            
            # Search vector database if available
            if self.vector_db and self.embeddings_model:
                vector_contexts = await self._search_vector_db(query, limit)
                contexts.extend(vector_contexts)
            
            # Search short-term memory
            short_term_contexts = self._search_short_term_memory(query, limit)
            contexts.extend(short_term_contexts)
            
            # Search long-term memory
            long_term_contexts = await self._search_long_term_memory(query, limit)
            contexts.extend(long_term_contexts)
            
            # Remove duplicates and format
            unique_contexts = []
            seen = set()
            
            for context in contexts:
                if context not in seen:
                    unique_contexts.append(context)
                    seen.add(context)
            
            return "\n\n".join(unique_contexts[:limit])
            
        except Exception as e:
            self.logger.error(f"Error getting relevant context: {e}")
            return ""
    
    async def _search_vector_db(self, query: str, limit: int) -> List[str]:
        """Search vector database for relevant memories"""
        try:
            if not self.vector_db or not self.embeddings_model:
                return []
            
            # Generate query embedding
            query_embedding = self.embeddings_model.encode(query).tolist()
            
            # Search ChromaDB
            results = self.vector_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            contexts = []
            for doc in results['documents'][0]:
                contexts.append(doc)
            
            return contexts
            
        except Exception as e:
            self.logger.error(f"Error searching vector database: {e}")
            return []
    
    def _search_short_term_memory(self, query: str, limit: int) -> List[str]:
        """Search short-term memory for relevant conversations"""
        try:
            contexts = []
            query_lower = query.lower()
            
            # Simple keyword search in short-term memory
            for interaction in reversed(self.short_term_memory):
                user_input = interaction['user_input'].lower()
                ai_response = interaction['ai_response'].lower()
                
                if (query_lower in user_input or query_lower in ai_response):
                    context = f"Previous: {interaction['user_input']} -> {interaction['ai_response']}"
                    contexts.append(context)
                    
                    if len(contexts) >= limit:
                        break
            
            return contexts
            
        except Exception as e:
            self.logger.error(f"Error searching short-term memory: {e}")
            return []
    
    async def _search_long_term_memory(self, query: str, limit: int) -> List[str]:
        """Search long-term SQLite database for relevant conversations"""
        try:
            contexts = []
            cursor = self.db_connection.cursor()
            
            # Simple text search in database
            cursor.execute('''
                SELECT user_input, ai_response, timestamp 
                FROM conversations 
                WHERE user_input LIKE ? OR ai_response LIKE ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            for row in cursor.fetchall():
                context = f"Previous ({row['timestamp']}): {row['user_input']} -> {row['ai_response']}"
                contexts.append(context)
            
            return contexts
            
        except Exception as e:
            self.logger.error(f"Error searching long-term memory: {e}")
            return []
    
    async def store_knowledge(self, content: str, source: str = "user", 
                             knowledge_type: str = "general", tags: List[str] = None):
        """Store knowledge in the knowledge base"""
        try:
            timestamp = datetime.now().isoformat()
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO knowledge 
                (content, content_hash, source, type, timestamp, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                content,
                content_hash,
                source,
                knowledge_type,
                timestamp,
                json.dumps(tags or []),
                json.dumps({})
            ))
            self.db_connection.commit()
            
            # Store in vector database
            if self.vector_db and self.embeddings_model:
                embedding = self.embeddings_model.encode(content).tolist()
                
                self.vector_collection.add(
                    documents=[content],
                    embeddings=[embedding],
                    metadatas=[{
                        "source": source,
                        "type": knowledge_type,
                        "timestamp": timestamp,
                        "tags": tags or []
                    }],
                    ids=[f"knowledge_{content_hash}"]
                )
            
            self.logger.info(f"Stored knowledge: {content[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Error storing knowledge: {e}")
    
    async def get_conversation_history(self, limit: int = 50) -> List[Dict]:
        """Get recent conversation history"""
        try:
            # Combine short-term and long-term memory
            history = []
            
            # Add short-term memory
            history.extend(self.short_term_memory)
            
            # Add recent long-term memory
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, user_input, ai_response, model_used, session_id
                FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit - len(self.short_term_memory),))
            
            for row in cursor.fetchall():
                history.append({
                    "role": "user",
                    "content": row['user_input'],
                    "timestamp": row['timestamp']
                })
                history.append({
                    "role": "assistant",
                    "content": row['ai_response'],
                    "timestamp": row['timestamp'],
                    "model": row['model_used']
                })
            
            # Sort by timestamp
            history.sort(key=lambda x: x.get('timestamp', ''))
            
            return history[-limit:]
            
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {e}")
            return []
    
    async def save_conversation_history(self, history: List[Dict]):
        """Save conversation history to long-term storage"""
        try:
            # Process history and store interactions
            for i in range(0, len(history), 2):
                if i + 1 < len(history):
                    user_msg = history[i]
                    ai_msg = history[i + 1]
                    
                    if user_msg.get('role') == 'user' and ai_msg.get('role') == 'assistant':
                        await self.store_interaction(
                            user_msg['content'],
                            ai_msg['content'],
                            ai_msg.get('model'),
                            user_msg.get('session_id')
                        )
            
            self.logger.info("Conversation history saved")
            
        except Exception as e:
            self.logger.error(f"Error saving conversation history: {e}")
    
    async def _auto_save_loop(self):
        """Automatic save loop for memory data"""
        interval = self.config.get('memory.auto_save_interval', 300)  # 5 minutes
        
        while True:
            try:
                await asyncio.sleep(interval)
                await self._save_short_term_memory()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in auto-save loop: {e}")
    
    async def _save_short_term_memory(self):
        """Save short-term memory to long-term storage"""
        try:
            if not self.short_term_memory:
                return
            
            # Move all short-term memory to long-term
            for interaction in self.short_term_memory:
                await self._store_to_long_term(interaction)
            
            self.short_term_memory.clear()
            self.logger.debug("Short-term memory saved to long-term storage")
            
        except Exception as e:
            self.logger.error(f"Error saving short-term memory: {e}")
    
    async def _handle_memory_store(self, event):
        """Handle memory store events"""
        try:
            data = event.data
            content = data.get('content')
            source = data.get('source', 'system')
            knowledge_type = data.get('type', 'general')
            tags = data.get('tags', [])
            
            if content:
                await self.store_knowledge(content, source, knowledge_type, tags)
                
        except Exception as e:
            self.logger.error(f"Error handling memory store event: {e}")
    
    async def _handle_memory_recall(self, event):
        """Handle memory recall events"""
        try:
            query = event.data.get('query', '')
            limit = event.data.get('limit', 5)
            
            if query:
                context = await self.get_relevant_context(query, limit)
                
                # Publish the recalled context
                await self.event_bus.publish(EventTypes.AI_RESPONSE, 
                                           {
                                               "type": "memory_recall",
                                               "context": context,
                                               "query": query
                                           }, 
                                           source="memory_manager")
                
        except Exception as e:
            self.logger.error(f"Error handling memory recall event: {e}")
    
    async def _handle_file_processed(self, event):
        """Handle processed file events to store knowledge"""
        try:
            file_path = event.data.get('file_path')
            content = event.data.get('content')
            file_type = event.data.get('type', 'file')
            
            if content:
                await self.store_knowledge(
                    content=content,
                    source=f"file:{file_path}",
                    knowledge_type=file_type,
                    tags=[file_type, "user_upload"]
                )
                
        except Exception as e:
            self.logger.error(f"Error handling file processed event: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current memory manager status"""
        try:
            # Get database statistics
            cursor = self.db_connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conversation_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM knowledge")
            knowledge_count = cursor.fetchone()[0]
            
            return {
                "short_term_memory": len(self.short_term_memory),
                "long_term_conversations": conversation_count,
                "knowledge_base_items": knowledge_count,
                "vector_db_available": self.vector_db is not None,
                "auto_save_enabled": self.config.get('memory.auto_save_interval') is not None,
                "memory_cache_size": len(self.memory_cache)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting memory status: {e}")
            return {"error": str(e)}
