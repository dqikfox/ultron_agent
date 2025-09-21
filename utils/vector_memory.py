import json
import logging
import uuid
from collections import deque
from typing import List, Dict, Any
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False
    logging.warning(
        "Vector search dependencies not available. "
        "Install: pip install sentence-transformers faiss-cpu"
    )

class VectorMemoryManager:
    """
    Advanced memory system with vector-based semantic search
    capabilities. Provides intelligent knowledge retrieval using
    embeddings and similarity search.
    """

    def __init__(self,
                 short_term_limit: int = 10,
                 vector_dim: int = 384,  # Dimension for sentence-transformers
                 index_file: str = 'vector_memory.index',
                 metadata_file: str = 'vector_memory.json',
                 model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the vector memory manager.

        Args:
            short_term_limit: Maximum items in short-term memory
            vector_dim: Dimension of embedding vectors
            index_file: File to store FAISS index
            metadata_file: File to store metadata
            model_name: Sentence transformer model name
        """
        self.short_term_memory = deque(maxlen=short_term_limit)
        self.vector_dim = vector_dim
        self.index_file = Path(index_file)
        self.metadata_file = Path(metadata_file)
        self.model_name = model_name

        # Initialize sentence transformer model
        self.embedding_model = None
        self.vector_index = None
        self.metadata_store: List[Dict[str, Any]] = []

        # Load or create vector search components
        if VECTOR_SEARCH_AVAILABLE:
            self._initialize_vector_search()
        else:
            logging.warning("Vector search not available - falling back to basic search")

        # Load existing data
        self._load_metadata()
        self._load_vector_index()

        logging.info(f"VectorMemoryManager initialized with {len(self.metadata_store)} stored items")

    def _initialize_vector_search(self):
        """Initialize the sentence transformer model and FAISS index."""
        try:
            if not self.embedding_model:
                logging.info(f"Loading sentence transformer model: {self.model_name}")
                self.embedding_model = SentenceTransformer(self.model_name)

            if not self.vector_index:
                if len(self.metadata_store) > 0:
                    # Load existing index
                    self._load_vector_index()
                else:
                    # Create new index
                    self.vector_index = faiss.IndexFlatIP(self.vector_dim)  # Inner product for cosine similarity

        except Exception as e:
            logging.error(f"Failed to initialize vector search: {e}")
            VECTOR_SEARCH_AVAILABLE = False

    def _load_metadata(self):
        """Load metadata from JSON file."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata_store = json.load(f)
                logging.info(f"Loaded {len(self.metadata_store)} metadata entries")
        except Exception as e:
            logging.error(f"Failed to load metadata: {e}")
            self.metadata_store = []

    def _save_metadata(self):
        """Save metadata to JSON file."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata_store, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save metadata: {e}")

    def _load_vector_index(self):
        """Load FAISS index from file."""
        try:
            if self.index_file.exists() and VECTOR_SEARCH_AVAILABLE:
                self.vector_index = faiss.read_index(str(self.index_file))
                logging.info(f"Loaded vector index with {self.vector_index.ntotal} vectors")
        except Exception as e:
            logging.error(f"Failed to load vector index: {e}")
            if VECTOR_SEARCH_AVAILABLE:
                self.vector_index = faiss.IndexFlatIP(self.vector_dim)

    def _save_vector_index(self):
        """Save FAISS index to file."""
        try:
            if self.vector_index and VECTOR_SEARCH_AVAILABLE:
                faiss.write_index(self.vector_index, str(self.index_file))
        except Exception as e:
            logging.error(f"Failed to save vector index: {e}")

    async def store_knowledge(self,
                            content: str,
                            source: str = "user",
                            knowledge_type: str = "conversation",
                            tags: List[str] = None,
                            metadata: Dict[str, Any] = None) -> str:
        """
        Store knowledge with vector embeddings for semantic search.

        Args:
            content: The knowledge content to store
            source: Source of the knowledge (user, system, api, etc.)
            knowledge_type: Type of knowledge (conversation, task, fact, etc.)
            tags: List of tags for categorization
            metadata: Additional metadata

        Returns:
            Unique ID of stored knowledge
        """
        try:
            knowledge_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()

            # Create metadata entry
            entry = {
                'id': knowledge_id,
                'content': content,
                'source': source,
                'type': knowledge_type,
                'tags': tags or [],
                'timestamp': timestamp,
                'metadata': metadata or {},
                'access_count': 0,
                'last_accessed': timestamp,
                'importance_score': self._calculate_importance(content, knowledge_type)
            }

            # Generate embedding if available
            if VECTOR_SEARCH_AVAILABLE and self.embedding_model:
                try:
                    embedding = self.embedding_model.encode(content, convert_to_numpy=True)
                    embedding = embedding.astype('float32')

                    # Normalize for cosine similarity
                    embedding = embedding / np.linalg.norm(embedding)

                    # Add to FAISS index
                    if self.vector_index:
                        self.vector_index.add(embedding.reshape(1, -1))

                    entry['has_embedding'] = True
                except Exception as e:
                    logging.error(f"Failed to generate embedding: {e}")
                    entry['has_embedding'] = False
            else:
                entry['has_embedding'] = False

            # Store metadata
            self.metadata_store.append(entry)
            self._save_metadata()

            # Add to short-term memory for recent context
            self.short_term_memory.append({
                'id': knowledge_id,
                'content': content[:100] + '...' if len(content) > 100 else content,
                'type': knowledge_type,
                'timestamp': timestamp
            })

            logging.info(f"Stored knowledge: {knowledge_id} ({knowledge_type})")
            return knowledge_id

        except Exception as e:
            logging.error(f"Failed to store knowledge: {e}")
            raise

    def _calculate_importance(self, content: str, knowledge_type: str) -> float:
        """Calculate importance score for knowledge prioritization."""
        base_score = 1.0

        # Type-based scoring
        type_scores = {
            'fact': 1.5,
            'task': 1.3,
            'conversation': 1.0,
            'error': 1.2,
            'solution': 1.4
        }
        base_score *= type_scores.get(knowledge_type, 1.0)

        # Content-based scoring
        content_length = len(content)
        if content_length > 500:
            base_score *= 1.2  # Longer content often more valuable
        elif content_length < 50:
            base_score *= 0.8  # Very short content less valuable

        # Keyword-based scoring
        important_keywords = ['error', 'solution', 'important', 'critical', 'security']
        keyword_count = sum(1 for keyword in important_keywords if keyword in content.lower())
        base_score *= (1 + keyword_count * 0.1)

        return min(base_score, 5.0)  # Cap at 5.0

    async def semantic_search(self,
                           query: str,
                           limit: int = 5,
                           similarity_threshold: float = 0.3,
                           knowledge_types: List[str] = None,
                           tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search using vector similarity.

        Args:
            query: Search query
            limit: Maximum results to return
            similarity_threshold: Minimum similarity score (0-1)
            knowledge_types: Filter by knowledge types
            tags: Filter by tags

        Returns:
            List of matching knowledge entries with similarity scores
        """
        try:
            if not VECTOR_SEARCH_AVAILABLE or not self.embedding_model or not self.vector_index:
                # Fallback to basic text search
                return self._basic_text_search(query, limit, knowledge_types, tags)

            # Generate query embedding
            query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)
            query_embedding = query_embedding.astype('float32')
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_embedding = query_embedding.reshape(1, -1)

            # Search FAISS index
            scores, indices = self.vector_index.search(query_embedding, min(limit * 2, len(self.metadata_store)))

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.metadata_store) and score >= similarity_threshold:
                    entry = self.metadata_store[idx].copy()
                    entry['similarity_score'] = float(score)

                    # Apply filters
                    if knowledge_types and entry['type'] not in knowledge_types:
                        continue
                    if tags and not any(tag in entry['tags'] for tag in tags):
                        continue

                    # Update access statistics
                    entry['access_count'] += 1
                    entry['last_accessed'] = datetime.now().isoformat()

                    results.append(entry)

            # Sort by similarity score and recency
            results.sort(key=lambda x: (x['similarity_score'], x['access_count']), reverse=True)
            results = results[:limit]

            # Save updated metadata
            self._save_metadata()

            return results

        except Exception as e:
            logging.error(f"Semantic search failed: {e}")
            return self._basic_text_search(query, limit, knowledge_types, tags)

    def _basic_text_search(self,
                          query: str,
                          limit: int,
                          knowledge_types: List[str] = None,
                          tags: List[str] = None) -> List[Dict[str, Any]]:
        """Fallback text-based search when vector search is unavailable."""
        query_lower = query.lower()
        results = []

        for entry in self.metadata_store:
            # Apply filters
            if knowledge_types and entry['type'] not in knowledge_types:
                continue
            if tags and not any(tag in entry['tags'] for tag in tags):
                continue

            # Simple text matching
            content_lower = entry['content'].lower()
            if query_lower in content_lower:
                score = len(query_lower) / len(content_lower)  # Simple relevance score
                entry_copy = entry.copy()
                entry_copy['similarity_score'] = score
                results.append(entry_copy)

        # Sort by score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:limit]

    async def get_relevant_context(self,
                                 query: str,
                                 max_items: int = 5,
                                 context_window: timedelta = timedelta(hours=24)) -> List[Dict[str, Any]]:
        """
        Get relevant context for a query, combining semantic search with recency.

        Args:
            query: Context query
            max_items: Maximum items to return
            context_window: Time window for recent context

        Returns:
            List of relevant context items
        """
        try:
            # Get semantic search results
            semantic_results = await self.semantic_search(query, limit=max_items*2)

            # Get recent context
            recent_context = self._get_recent_context(context_window, max_items)

            # Combine and deduplicate
            combined = []
            seen_ids = set()

            # Add semantic results first
            for result in semantic_results:
                if result['id'] not in seen_ids:
                    combined.append(result)
                    seen_ids.add(result['id'])

            # Add recent context if not already included
            for item in recent_context:
                if item['id'] not in seen_ids:
                    combined.append(item)
                    seen_ids.add(item)

            # Sort by recency and relevance
            combined.sort(key=lambda x: (
                x.get('similarity_score', 0),
                datetime.fromisoformat(x['timestamp'])
            ), reverse=True)

            return combined[:max_items]

        except Exception as e:
            logging.error(f"Failed to get relevant context: {e}")
            return []

    def _get_recent_context(self, time_window: timedelta, limit: int) -> List[Dict[str, Any]]:
        """Get recent context within the specified time window."""
        cutoff_time = datetime.now() - time_window
        recent_items = []

        for entry in self.metadata_store:
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if entry_time >= cutoff_time:
                recent_items.append(entry)

        # Sort by timestamp (most recent first)
        recent_items.sort(key=lambda x: x['timestamp'], reverse=True)
        return recent_items[:limit]

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        total_items = len(self.metadata_store)
        types_count = {}
        sources_count = {}
        tags_count = {}

        for entry in self.metadata_store:
            # Count by type
            entry_type = entry.get('type', 'unknown')
            types_count[entry_type] = types_count.get(entry_type, 0) + 1

            # Count by source
            source = entry.get('source', 'unknown')
            sources_count[source] = sources_count.get(source, 0) + 1

            # Count tags
            for tag in entry.get('tags', []):
                tags_count[tag] = tags_count.get(tag, 0) + 1

        # Calculate access patterns
        total_accesses = sum(entry.get('access_count', 0) for entry in self.metadata_store)
        avg_accesses = total_accesses / max(total_items, 1)

        return {
            'total_items': total_items,
            'types_distribution': types_count,
            'sources_distribution': sources_count,
            'popular_tags': dict(sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            'total_accesses': total_accesses,
            'avg_accesses_per_item': round(avg_accesses, 2),
            'vector_search_enabled': VECTOR_SEARCH_AVAILABLE and self.vector_index is not None,
            'embedding_model': self.model_name if self.embedding_model else None
        }

    async def cleanup_old_knowledge(self, days_to_keep: int = 90):
        """Clean up old, low-importance knowledge to manage memory size."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            items_to_remove = []

            for i, entry in enumerate(self.metadata_store):
                entry_date = datetime.fromisoformat(entry['timestamp'])
                importance = entry.get('importance_score', 1.0)
                access_count = entry.get('access_count', 0)

                # Remove if old, low importance, and rarely accessed
                if (entry_date < cutoff_date and
                    importance < 2.0 and
                    access_count < 3):
                    items_to_remove.append(i)

            # Remove from metadata store (in reverse order to maintain indices)
            for i in reversed(items_to_remove):
                del self.metadata_store[i]

            if items_to_remove:
                logging.info(f"Cleaned up {len(items_to_remove)} old knowledge items")
                self._save_metadata()

                # Rebuild vector index if needed
                if VECTOR_SEARCH_AVAILABLE and items_to_remove:
                    await self._rebuild_vector_index()

        except Exception as e:
            logging.error(f"Failed to cleanup old knowledge: {e}")

    async def _rebuild_vector_index(self):
        """Rebuild the FAISS index after cleanup or corruption."""
        try:
            if not VECTOR_SEARCH_AVAILABLE or not self.embedding_model:
                return

            # Create new index
            self.vector_index = faiss.IndexFlatIP(self.vector_dim)

            # Re-add all embeddings
            embeddings = []
            valid_entries = []

            for entry in self.metadata_store:
                if entry.get('has_embedding', False):
                    try:
                        embedding = self.embedding_model.encode(entry['content'], convert_to_numpy=True)
                        embedding = embedding.astype('float32')
                        embedding = embedding / np.linalg.norm(embedding)
                        embeddings.append(embedding)
                        valid_entries.append(entry)
                    except Exception as e:
                        logging.warning(f"Failed to re-encode entry {entry['id']}: {e}")

            if embeddings:
                embeddings_array = np.array(embeddings)
                self.vector_index.add(embeddings_array)

            logging.info(f"Rebuilt vector index with {len(valid_entries)} entries")

        except Exception as e:
            logging.error(f"Failed to rebuild vector index: {e}")

    def save_state(self):
        """Save the complete memory state."""
        try:
            self._save_metadata()
            self._save_vector_index()
            logging.info("Vector memory state saved successfully")
        except Exception as e:
            logging.error(f"Failed to save memory state: {e}")

    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.save_state()
        except:
            pass