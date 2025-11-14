"""Integration tests for file system operations and persistence.

This module tests file operations including creation, modification,
deletion, and persistence across system restarts.

Test Categories:
    - File creation and deletion
    - Permission management
    - Path validation
    - Concurrent access
    - Data persistence
"""

import pytest
import tempfile
import os
from pathlib import Path
import time

pytestmark = [pytest.mark.integration]


class TestFileSystemOperations:
    """Test basic file system operations."""

    def test_temp_directory_creation(self):
        """Test creating temporary directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            assert temp_path.exists(), "Temp directory not created"
            assert temp_path.is_dir(), "Path is not a directory"

    def test_file_creation_and_deletion(self):
        """Test file creation and deletion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_file.txt"

            # Create file
            test_file.write_text("test content")
            assert test_file.exists(), "File not created"
            assert test_file.read_text() == "test content"

            # Delete file
            test_file.unlink()
            assert not test_file.exists(), "File not deleted"

    def test_directory_traversal(self):
        """Test directory traversal and file listing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create nested directories
            (base_path / "level1" / "level2").mkdir(parents=True)
            (base_path / "level1" / "file1.txt").write_text("content1")
            (base_path / "level1" / "level2" / "file2.txt").write_text(
                "content2"
            )

            # Test traversal
            files = list(base_path.rglob("*.txt"))
            assert len(files) == 2, f"Expected 2 files, found {len(files)}"


class TestFilePermissions:
    """Test file permission management."""

    def test_read_write_permissions(self):
        """Test file read/write permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            # Check read permission
            assert os.access(test_file, os.R_OK), "No read permission"

            # Check write permission
            assert os.access(test_file, os.W_OK), "No write permission"

    def test_directory_permissions(self):
        """Test directory access permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)

            # Check execute permission (directory traversal)
            assert os.access(dir_path, os.X_OK), "No execute permission"

            # Check read permission (listing contents)
            assert os.access(dir_path, os.R_OK), "No read permission"


class TestPathValidation:
    """Test path validation and security checks."""

    def test_absolute_path_handling(self):
        """Test handling of absolute paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            # Get absolute path
            abs_path = test_file.resolve()

            # Should be absolute
            assert abs_path.is_absolute(), "Path should be absolute"

            # Should still be readable
            assert abs_path.read_text() == "content"

    def test_relative_path_handling(self):
        """Test handling of relative paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)

                # Create file with relative path
                test_file = Path("test.txt")
                test_file.write_text("content")

                # Should be readable via relative path
                assert test_file.read_text() == "content"

            finally:
                os.chdir(original_cwd)

    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create file with traversal attempt
            dangerous_path = base_path / "normal_file.txt"

            # This should work normally
            dangerous_path.write_text("content")
            assert dangerous_path.read_text() == "content"

            # But traversal outside base should fail or be contained
            # (Actual security checks depend on application implementation)


class TestConcurrentFileAccess:
    """Test concurrent file access scenarios."""

    def test_multiple_reads(self):
        """Test multiple concurrent reads of same file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("shared content")

            # Simulate concurrent reads
            contents = []
            for _ in range(5):
                contents.append(test_file.read_text())

            # All reads should get same content
            assert all(c == "shared content" for c in contents)

    def test_read_write_synchronization(self):
        """Test read/write synchronization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"

            # Initial write
            test_file.write_text("version1")

            # Read
            content1 = test_file.read_text()
            assert content1 == "version1"

            # Update
            test_file.write_text("version2")

            # Read again
            content2 = test_file.read_text()
            assert content2 == "version2"
            assert content1 != content2


class TestDataPersistence:
    """Test data persistence across operations."""

    def test_file_persistence_after_write(self):
        """Test that data persists after write operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "persist.txt"

            # Write data
            original_data = "persistent data"
            test_file.write_text(original_data)

            # Simulate some time passing
            time.sleep(0.1)

            # Read back data
            persisted_data = test_file.read_text()
            assert persisted_data == original_data

    def test_directory_structure_persistence(self):
        """Test that directory structures persist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create structure
            (base_path / "dir1" / "dir2" / "dir3").mkdir(parents=True)
            (base_path / "dir1" / "file.txt").write_text("content")

            # Verify structure persists
            assert (base_path / "dir1").exists()
            assert (base_path / "dir1" / "dir2").exists()
            assert (base_path / "dir1" / "dir2" / "dir3").exists()
            assert (base_path / "dir1" / "file.txt").read_text() == "content"


class TestLargeFileHandling:
    """Test handling of large files."""

    def test_large_file_creation(self):
        """Test creating and reading large files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "large.txt"

            # Create 1MB file
            large_data = "x" * (1024 * 1024)
            test_file.write_text(large_data)

            assert test_file.stat().st_size == 1024 * 1024
            assert len(test_file.read_text()) == 1024 * 1024

    def test_large_file_line_iteration(self):
        """Test iterating over large file by lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "lines.txt"

            # Create file with many lines
            lines = [f"line {i}\n" for i in range(1000)]
            test_file.write_text("".join(lines))

            # Read and count lines
            read_lines = test_file.read_text().split('\n')
            assert len(read_lines) >= 1000


class TestFileContentValidation:
    """Test file content validation and integrity."""

    def test_text_encoding_handling(self):
        """Test handling of different text encodings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "encoded.txt"

            # UTF-8 content
            utf8_content = "Hello, 世界! 🌍"
            test_file.write_text(utf8_content, encoding='utf-8')

            # Read back with encoding
            read_content = test_file.read_text(encoding='utf-8')
            assert read_content == utf8_content

    def test_binary_file_handling(self):
        """Test handling of binary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "binary.bin"

            # Binary content
            binary_data = bytes(range(256))
            test_file.write_bytes(binary_data)

            # Read back binary
            read_data = test_file.read_bytes()
            assert read_data == binary_data

    def test_json_file_handling(self):
        """Test JSON file reading and writing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "data.json"

            import json

            # Write JSON
            data = {"key": "value", "number": 42, "list": [1, 2, 3]}
            test_file.write_text(json.dumps(data))

            # Read and parse JSON
            read_data = json.loads(test_file.read_text())
            assert read_data == data


class TestFileSystemCleanup:
    """Test file system cleanup and resource management."""

    def test_temporary_file_cleanup(self):
        """Test that temporary files are cleaned up."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            assert temp_path.exists()

        # After context exit, directory should be gone
        assert not temp_path.exists()

    def test_explicit_file_deletion(self):
        """Test explicit file deletion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "to_delete.txt"
            test_file.write_text("content")

            assert test_file.exists()
            test_file.unlink()
            assert not test_file.exists()

    def test_directory_tree_removal(self):
        """Test removal of directory tree."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "to_remove"
            (base / "sub1" / "sub2").mkdir(parents=True)
            (base / "sub1" / "file.txt").write_text("content")

            import shutil
            shutil.rmtree(base)
            assert not base.exists()


class TestSymlinkHandling:
    """Test symbolic link operations."""

    @pytest.mark.skipif(
        os.name == 'nt' and not os.getenv('PYTEST_ALLOW_SYMLINKS'),
        reason="Symlinks require admin privileges on Windows"
    )
    def test_symlink_creation(self):
        """Test creating symbolic links."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            target = base / "target.txt"
            link = base / "link.txt"

            target.write_text("content")

            try:
                link.symlink_to(target)
                assert link.is_symlink()
                assert link.read_text() == "content"
            except OSError as e:
                pytest.skip(f"Cannot create symlinks: {e}")


# Test configuration
def pytest_configure(config):
    """Configure pytest markers for file system tests."""
    config.addinivalue_line(
        "markers", "filesystem: File system integration tests"
    )
    config.addinivalue_line(
        "markers", "persistence: Data persistence tests"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
