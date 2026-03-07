"""
Test suite for enhanced semantic memory system
Tests vector embeddings, similarity search, and memory persistence
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from enhanced_memory_system import EnhancedMemorySystem


class TestSemanticMemory:
    """Test semantic memory with vector embeddings"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_memory.db")
            yield db_path

    @pytest.fixture
    def memory_system(self, temp_db):
        """Initialize memory system with test database"""
        return EnhancedMemorySystem(db_path=temp_db)

    def test_memory_initialization(self, memory_system):
        """Test that memory system initializes correctly"""
        assert memory_system is not None
        assert memory_system.db_path.endswith("test_memory.db")

    def test_store_conversation(self, memory_system):
        """Test storing a conversation"""
        user_input = "What is the capital of France?"
        agent_response = "The capital of France is Paris."
        context = {"topic": "geography", "language": "en"}

        memory_system.store_conversation(user_input, agent_response, context)
        # If no exception, test passes

    def test_retrieve_similar_conversations(self, memory_system):
        """Test retrieving similar conversations using vector similarity"""
        # Store several conversations
        conversations = [
            ("What is the capital of France?", "The capital of France is Paris."),
            ("What is the capital of Germany?", "The capital of Germany is Berlin."),
            ("What is the capital of Spain?", "The capital of Spain is Madrid."),
            ("How do I cook pasta?", "Boil water, add pasta, cook for 8-10 minutes."),
            ("What is Python?", "Python is a programming language."),
        ]

        for user_input, agent_response in conversations:
            memory_system.store_conversation(user_input, agent_response)

        # Query for similar conversations
        query = "What is the capital of Italy?"
        results = memory_system.retrieve_similar_conversations(query, limit=3)

        # Should retrieve capital-related conversations
        assert len(results) <= 3
        assert all("similarity" in r for r in results)
        assert all("user_input" in r for r in results)

    def test_similarity_ranking(self, memory_system):
        """Test that similar conversations are ranked higher"""
        # Store conversations with varying similarity
        memory_system.store_conversation(
            "What is Python?",
            "Python is a programming language."
        )
        memory_system.store_conversation(
            "How do you use Python?",
            "Python is used for web development, data science, etc."
        )
        memory_system.store_conversation(
            "What is cooking?",
            "Cooking is the process of preparing food."
        )

        # Query about Python
        query = "Tell me about Python programming"
        results = memory_system.retrieve_similar_conversations(query, limit=3)

        # Python-related results should have higher similarity
        if len(results) > 1:
            # Earlier results (higher similarity) should be more about Python
            assert "python" in results[0]["user_input"].lower()

    def test_conversation_summary(self, memory_system):
        """Test generating conversation summary"""
        memory_system.store_conversation(
            "How do I deploy code?",
            "Use CI/CD pipelines for deployment."
        )
        memory_system.store_conversation(
            "What is AWS?",
            "AWS is Amazon Web Services cloud platform."
        )

        summary = memory_system.get_conversation_summary(days=7)
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_embedding_consistency(self, memory_system):
        """Test that embeddings are consistent"""
        text = "Hello world"
        embedding1 = memory_system._create_simple_embedding(text)
        embedding2 = memory_system._create_simple_embedding(text)

        # Embeddings of same text should be identical
        assert (embedding1 == embedding2).all()

    def test_cosine_similarity_calculation(self, memory_system):
        """Test cosine similarity calculation"""
        import numpy as np

        # Create simple test vectors
        a = np.array([1, 0, 0], dtype=np.float32)
        b = np.array([1, 0, 0], dtype=np.float32)
        c = np.array([0, 1, 0], dtype=np.float32)

        # Same vectors should have similarity of 1.0
        sim_aa = memory_system._cosine_similarity(a, a)
        assert abs(sim_aa - 1.0) < 0.001

        # Orthogonal vectors should have similarity near 0.0
        sim_ac = memory_system._cosine_similarity(a, c)
        assert abs(sim_ac) < 0.001

    def test_context_preservation(self, memory_system):
        """Test that context is preserved in storage"""
        user_input = "What is AI?"
        agent_response = "AI is artificial intelligence."
        context = {
            "confidence": 0.95,
            "domain": "technology",
            "tool_used": "knowledge_base"
        }

        memory_system.store_conversation(user_input, agent_response, context)
        results = memory_system.retrieve_similar_conversations(user_input, limit=1)

        assert len(results) > 0
        stored_context = results[0]["context"]
        assert stored_context["confidence"] == 0.95
        assert stored_context["domain"] == "technology"

    def test_empty_retrieval(self, memory_system):
        """Test retrieving when memory is empty"""
        results = memory_system.retrieve_similar_conversations("Test query", limit=5)
        assert results == []

    @pytest.mark.asyncio
    async def test_semantic_search_performance(self, memory_system):
        """Test that semantic search performs well"""
        import time

        # Store multiple conversations
        for i in range(20):
            memory_system.store_conversation(
                f"Question {i}: about topic {i % 5}",
                f"Answer {i}: response about topic {i % 5}"
            )

        # Measure search time
        start = time.time()
        results = memory_system.retrieve_similar_conversations("about topic 2", limit=5)
        elapsed = time.time() - start

        # Search should be fast (< 1 second for 20 entries)
        assert elapsed < 1.0
        assert len(results) <= 5


class TestMemoryIntegration:
    """Test semantic memory integration with agent systems"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_integration.db")
            yield db_path

    @pytest.fixture
    def memory_system(self, temp_db):
        """Initialize memory system"""
        return EnhancedMemorySystem(db_path=temp_db)

    def test_multi_session_memory(self, memory_system):
        """Test that memory persists across sessions"""
        # Session 1: Store conversation
        memory_system.store_conversation(
            "Remember this important fact",
            "The sky is blue"
        )

        # Session 2: Create new instance pointing to same database
        memory_system_2 = EnhancedMemorySystem(db_path=memory_system.db_path)

        # Should retrieve conversation from previous session
        results = memory_system_2.retrieve_similar_conversations(
            "Remember this important fact",  # Exact match query
            limit=1
        )

        assert len(results) > 0
        assert "remember" in results[0]["user_input"].lower()

    def test_decision_memory_recall(self, memory_system):
        """Test recalling past decisions for current decision-making"""
        # Store decision history
        decisions = [
            ("Should we use Python?", "Yes, Python is good for this project"),
            ("Should we use Docker?", "Yes, Docker simplifies deployment"),
            ("Should we use Kubernetes?", "Maybe, it depends on scale"),
        ]

        for question, decision in decisions:
            memory_system.store_conversation(question, decision)

        # New question about technology choice
        new_query = "What technology stack should we use?"
        results = memory_system.retrieve_similar_conversations(new_query, limit=3)

        # Should recall related technology decisions
        assert len(results) > 0
        recalled_text = " ".join([r["user_input"] + " " + r["agent_response"] for r in results])
        assert any(tech in recalled_text.lower() for tech in ["python", "docker", "kubernetes"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
