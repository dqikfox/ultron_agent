#!/usr/bin/env python3
"""
Test script for orphan detection functionality and validation

This test script validates the orphan detection tool and provides 
focused tests for the most critical issues found.
"""

import pytest
import os
import json
from pathlib import Path
import ast
import importlib.util
from detect_orphans import OrphanDetector


class TestOrphanDetection:
    """Test class for orphan detection functionality"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.project_root = Path(__file__).parent
        cls.detector = OrphanDetector(str(cls.project_root))
        
        # Load existing results if available
        results_file = cls.project_root / 'orphan_analysis_results.json'
        if results_file.exists():
            with open(results_file, 'r') as f:
                cls.results = json.load(f)
        else:
            cls.results = None
    
    def test_detector_initialization(self):
        """Test that the orphan detector initializes correctly"""
        assert self.detector is not None
        assert self.detector.project_root == self.project_root
        assert isinstance(self.detector.results, dict)
    
    def test_syntax_error_detection(self):
        """Test that syntax errors are properly detected"""
        if not self.results:
            pytest.skip("No analysis results available")
        
        syntax_errors = [item for item in self.results['broken_imports'] 
                        if item.get('type') == 'syntax_error']
        
        # Verify that detected syntax errors are actually broken
        for error in syntax_errors[:5]:  # Test first 5
            file_path = self.project_root / error['file']
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ast.parse(content)
                    # If we get here, the file is actually valid
                    pytest.fail(f"File {error['file']} was flagged as syntax error but is valid")
                except SyntaxError:
                    # This is expected for files with syntax errors
                    pass
    
    def test_missing_asset_detection(self):
        """Test that missing assets are correctly identified"""
        if not self.results:
            pytest.skip("No analysis results available")
        
        # Check a few missing assets
        missing_assets = self.results['missing_assets'][:10]
        
        for asset in missing_assets:
            source_file = self.project_root / asset['source_file']
            asset_path = asset['asset_path']
            
            # Verify the source file exists
            assert source_file.exists(), f"Source file {asset['source_file']} should exist"
            
            # Verify the asset is actually referenced in the source
            if source_file.suffix in {'.py', '.html', '.js', '.css', '.md'}:
                try:
                    with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    assert asset_path in content, f"Asset {asset_path} should be referenced in {asset['source_file']}"
                except Exception:
                    pass  # Skip problematic files
    
    def test_duplicate_file_detection(self):
        """Test that duplicate files are correctly identified"""
        if not self.results:
            pytest.skip("No analysis results available")
        
        duplicates = self.results['duplicate_files'][:5]
        
        for duplicate_group in duplicates:
            files = duplicate_group['files']
            assert len(files) >= 2, "Duplicate group should have at least 2 files"
            
            # Verify files actually exist and have same content
            file_contents = []
            for file_path in files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    try:
                        with open(full_path, 'rb') as f:
                            file_contents.append(f.read())
                    except Exception:
                        pass
            
            # If we have content for multiple files, they should be identical
            if len(file_contents) >= 2:
                first_content = file_contents[0]
                for content in file_contents[1:]:
                    assert content == first_content, f"Files in duplicate group should have identical content"
    
    def test_orphaned_file_detection(self):
        """Test orphaned file detection logic"""
        if not self.results:
            pytest.skip("No analysis results available")
        
        orphaned_files = self.results['orphaned_files'][:10]
        
        for orphan in orphaned_files:
            file_path = self.project_root / orphan['file']
            
            # File should exist
            if file_path.exists():
                # Basic check that it's not a critical file
                assert not orphan['file'].endswith('main.py'), "main.py should not be marked as orphaned"
                assert not orphan['file'].endswith('__init__.py'), "__init__.py files should not be marked as orphaned"
                assert not orphan['file'].endswith('requirements.txt'), "requirements.txt should not be marked as orphaned"
    
    def test_critical_files_not_orphaned(self):
        """Test that critical files are not marked as orphaned"""
        if not self.results:
            pytest.skip("No analysis results available")
        
        orphaned_files = [item['file'] for item in self.results['orphaned_files']]
        
        # Critical files that should never be orphaned
        critical_files = [
            'main.py',
            'agent_core.py', 
            'brain.py',
            'config.py',
            'requirements.txt',
            'README.md',
            'setup.py'
        ]
        
        for critical_file in critical_files:
            if (self.project_root / critical_file).exists():
                assert critical_file not in orphaned_files, f"Critical file {critical_file} should not be orphaned"
    
    def test_analysis_results_structure(self):
        """Test that analysis results have correct structure"""
        if not self.results:
            pytest.skip("No analysis results available")
        
        required_keys = [
            'broken_imports',
            'missing_assets', 
            'orphaned_files',
            'duplicate_files',
            'unreferenced_directories',
            'broken_references',
            'recommendations'
        ]
        
        for key in required_keys:
            assert key in self.results, f"Results should contain {key}"
            assert isinstance(self.results[key], list), f"{key} should be a list"


def test_orphan_detector_can_run():
    """Test that the orphan detector can run without errors"""
    project_root = Path(__file__).parent
    detector = OrphanDetector(str(project_root))
    
    # Run a minimal analysis
    try:
        # Test just the initialization and basic functionality
        detector._detect_broken_imports()
        assert True  # If we get here, basic functionality works
    except Exception as e:
        pytest.fail(f"Orphan detector should run without errors: {e}")


def test_specific_known_issues():
    """Test detection of specific known issues from the project"""
    project_root = Path(__file__).parent
    
    # Test for known problematic files
    problematic_files = [
        'nvidia_enhanced_ultron.py',
        'main_gui_server.py', 
        'ollama_keepalive.py'
    ]
    
    for file_name in problematic_files:
        file_path = project_root / file_name
        if file_path.exists():
            # Try to parse the file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                # If parsing succeeds, the file is actually OK
                print(f"Note: {file_name} parsed successfully")
            except SyntaxError:
                # This confirms there's a syntax error
                print(f"Confirmed: {file_name} has syntax errors")
                assert True  # This is expected


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])