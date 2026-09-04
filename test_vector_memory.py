#!/usr/bin/env python3
"""
Test script for VectorMemoryManager
"""
import asyncio
import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from vector_memory import VectorMemoryManager

async def test_vector_memory():
    """Test the vector memory system."""
    print("Testing VectorMemoryManager...")

    # Initialize memory manager
    memory = VectorMemoryManager(
        short_term_limit=5,
        index_file='test_vector_memory.index',
        metadata_file='test_vector_memory.json'
    )

    # Test storing knowledge
    print("\n1. Testing knowledge storage...")
    knowledge_id = await memory.store_knowledge(
        content="Python is a high-level programming language known for its simplicity and readability.",
        source="test",
        knowledge_type="fact",
        tags=["python", "programming", "language"]
    )
    print(f"Stored knowledge with ID: {knowledge_id}")

    # Store more knowledge
    await memory.store_knowledge(
        content="Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
        source="test",
        knowledge_type="fact",
        tags=["ml", "ai", "learning"]
    )

    await memory.store_knowledge(
        content="Error handling is crucial for robust software development.",
        source="test",
        knowledge_type="solution",
        tags=["error", "handling", "software"]
    )

    # Test semantic search
    print("\n2. Testing semantic search...")
    results = await memory.semantic_search("programming languages", limit=3)
    print(f"Found {len(results)} results for 'programming languages':")
    for result in results:
        print(f"  - {result['content'][:50]}... (score: {result.get('similarity_score', 0):.3f})")

    # Test basic text search (fallback)
    print("\n3. Testing basic text search...")
    basic_results = memory._basic_text_search("error", limit=2)
    print(f"Found {len(basic_results)} basic results for 'error':")
    for result in basic_results:
        print(f"  - {result['content'][:50]}... (score: {result.get('similarity_score', 0):.3f})")

    # Test memory statistics
    print("\n4. Testing memory statistics...")
    stats = memory.get_memory_stats()
    print("Memory Statistics:")
    print(f"  - Total items: {stats['total_items']}")
    print(f"  - Types: {stats['types_distribution']}")
    print(f"  - Vector search enabled: {stats['vector_search_enabled']}")

    # Test relevant context
    print("\n5. Testing relevant context...")
    context = await memory.get_relevant_context("artificial intelligence", max_items=2)
    print(f"Found {len(context)} relevant context items:")
    for item in context:
        print(f"  - {item['content'][:50]}...")

    # Save state
    print("\n6. Saving memory state...")
    memory.save_state()
    print("Memory state saved successfully")

    print("\n✅ VectorMemoryManager test completed successfully!")

if __name__ == "__main__":
    try:
    asyncio.run(test_vector_memory())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
