"""
Comprehensive tests for Memory class
"""
import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open
from memory import Memory


class TestMemory:
    """Test suite for Memory class"""

    def test_memory_initialization_default(self):
        """Test memory initialization with default parameters"""
        with patch('memory.Memory.load_long_term_memory', return_value={}):
            memory = Memory()
            assert memory.short_term_memory.maxlen == 10
            assert len(memory.short_term_memory) == 0
            assert len(memory.long_term_memory) == 0

    def test_memory_initialization_custom(self):
        """Test memory initialization with custom parameters"""
        with patch('memory.Memory.load_long_term_memory', return_value={}):
            memory = Memory(short_term_limit=5, long_term_file='custom.json')
            assert memory.short_term_memory.maxlen == 5

    def test_add_to_short_term(self):
        """Test adding items to short-term memory"""
        with patch('memory.Memory.load_long_term_memory', return_value={}):
            memory = Memory(short_term_limit=3)
            memory.add_to_short_term("item1")
            memory.add_to_short_term("item2")
            
            assert len(memory.short_term_memory) == 2
            assert "item1" in memory.short_term_memory
            assert "item2" in memory.short_term_memory

    def test_add_to_short_term_overflow(self):
        """Test short-term memory overflow behavior"""
        with patch('memory.Memory.load_long_term_memory', return_value={}):
            memory = Memory(short_term_limit=2)
            memory.add_to_short_term("item1")
            memory.add_to_short_term("item2")
            memory.add_to_short_term("item3")  # Should remove oldest
            
            assert len(memory.short_term_memory) == 2
            assert "item1" not in memory.short_term_memory
            assert "item2" in memory.short_term_memory
            assert "item3" in memory.short_term_memory

    def test_add_to_long_term(self):
        """Test adding items to long-term memory"""
        with patch('memory.Memory.load_long_term_memory', return_value={}):
            memory = Memory()
            memory.add_to_long_term("long_term_item")
            
            assert len(memory.long_term_memory) == 1
            assert "long_term_item" in memory.long_term_memory.values()

    def test_retrieve_short_term(self):
        """Test retrieving short-term memory"""
        memory = Memory()
        memory.add_to_short_term("item1")
        memory.add_to_short_term("item2")
        
        retrieved = memory.retrieve_short_term()
        assert len(retrieved) == 2
        assert "item1" in retrieved
        assert "item2" in retrieved

    def test_retrieve_long_term(self):
        """Test retrieving long-term memory"""
        memory = Memory()
        memory.add_to_long_term("long_item1")
        memory.add_to_long_term("long_item2")
        
        retrieved = memory.retrieve_long_term()
        assert len(retrieved) == 2
        assert "long_item1" in retrieved
        assert "long_item2" in retrieved

    def test_get_recent_memory_default(self):
        """Test getting recent memory with default limit"""
        memory = Memory()
        for i in range(10):
            memory.add_to_short_term(f"item{i}")
        
        recent = memory.get_recent_memory()
        assert len(recent) == 5  # Default limit

    def test_get_recent_memory_custom_limit(self):
        """Test getting recent memory with custom limit"""
        memory = Memory()
        for i in range(10):
            memory.add_to_short_term(f"item{i}")
        
        recent = memory.get_recent_memory(limit=3)
        assert len(recent) == 3

    def test_get_recent_memory_less_than_limit(self):
        """Test getting recent memory when items are less than limit"""
        memory = Memory()
        memory.add_to_short_term("item1")
        memory.add_to_short_term("item2")
        
        recent = memory.get_recent_memory(limit=5)
        assert len(recent) == 2

    def test_clear_short_term(self):
        """Test clearing short-term memory"""
        memory = Memory()
        memory.add_to_short_term("item1")
        memory.add_to_short_term("item2")
        
        memory.clear_short_term()
        assert len(memory.short_term) == 0

    def test_clear_long_term(self):
        """Test clearing long-term memory"""
        memory = Memory()
        memory.add_to_long_term("item1")
        memory.add_to_long_term("item2")
        
        memory.clear_long_term()
        assert len(memory.long_term) == 0

    def test_search_memory_found(self):
        """Test searching memory when items are found"""
        memory = Memory()
        memory.add_to_short_term("hello world")
        memory.add_to_short_term("goodbye world")
        memory.add_to_long_term("hello universe")
        
        results = memory.search_memory("hello")
        assert len(results) == 2
        assert "hello world" in results
        assert "hello universe" in results

    def test_search_memory_not_found(self):
        """Test searching memory when no items are found"""
        memory = Memory()
        memory.add_to_short_term("hello world")
        memory.add_to_long_term("goodbye universe")
        
        results = memory.search_memory("nonexistent")
        assert len(results) == 0

    def test_save_long_term_memory(self):
        """Test saving long-term memory to file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            memory = Memory(long_term_file=tmp_path)
            memory.add_to_long_term("test_item")
            memory.save_long_term_memory(tmp_path)
            
            # Verify file was written
            with open(tmp_path, 'r') as f:
                data = json.load(f)
                assert "test_item" in data
        finally:
            os.unlink(tmp_path)

    def test_load_long_term_memory_file_exists(self):
        """Test loading long-term memory when file exists"""
        test_data = ["item1", "item2", "item3"]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            json.dump(test_data, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            memory = Memory()
            memory.load_long_term_memory(tmp_path)
            
            assert len(memory.long_term) == 3
            assert "item1" in memory.long_term
            assert "item2" in memory.long_term
            assert "item3" in memory.long_term
        finally:
            os.unlink(tmp_path)

    def test_load_long_term_memory_file_not_exists(self):
        """Test loading long-term memory when file doesn't exist"""
        memory = Memory()
        memory.load_long_term_memory("nonexistent_file.json")
        
        # Should not crash and memory should remain empty
        assert len(memory.long_term) == 0

    def test_load_long_term_memory_invalid_json(self):
        """Test loading long-term memory with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            tmp_file.write("invalid json content")
            tmp_path = tmp_file.name
        
        try:
            memory = Memory()
            memory.load_long_term_memory(tmp_path)
            
            # Should handle gracefully and keep memory empty
            assert len(memory.long_term) == 0
        finally:
            os.unlink(tmp_path)

    def test_memory_integration(self):
        """Test complete memory workflow"""
        memory = Memory(short_term_limit=3)
        
        # Add items to both memories
        memory.add_to_short_term("short1")
        memory.add_to_short_term("short2")
        memory.add_to_long_term("long1")
        memory.add_to_long_term("long2")
        
        # Test search across both
        results = memory.search_memory("short")
        assert len(results) == 2
        
        # Test recent memory
        recent = memory.get_recent_memory(limit=1)
        assert len(recent) == 1
        assert "short2" in recent
        
        # Test clearing
        memory.clear_short_term()
        memory.clear_long_term()
        
        assert len(memory.short_term) == 0
        assert len(memory.long_term) == 0
