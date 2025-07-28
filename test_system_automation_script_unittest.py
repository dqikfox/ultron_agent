import unittest
import os
import shutil
import time
from system_automation_script import (
    run_diagnostics, create_file, edit_file, delete_file, list_files
)

class TestSystemAutomationScript(unittest.TestCase):
    def setUp(self):
        self.test_dir = "automated_files"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        # Clean up test dir
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))

    def tearDown(self):
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))

    def test_run_diagnostics(self):
        result = run_diagnostics()
        self.assertIn("CPU Usage", result)
        self.assertIn("Memory Usage", result)
        self.assertIn("Disk Usage", result)
        self.assertIn("Running Processes", result)

    def test_create_edit_delete_file(self):
        fname = f"testfile_{int(time.time())}"
        content = "Hello, world!"
        # Create
        res_create = create_file(fname, content)
        self.assertIn("File created", res_create)
        # Edit
        res_edit = edit_file(fname, "Appended text")
        self.assertIn("File edited", res_edit)
        # List
        files = list_files()
        self.assertIn(fname, files)
        # Delete
        res_delete = delete_file(fname)
        self.assertIn("File deleted", res_delete)
        # List after delete
        files_after = list_files()
        self.assertNotIn(fname, files_after)

    def test_list_files_empty(self):
        # Clean up
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        files = list_files()
        self.assertIn("No files found", files)

if __name__ == "__main__":
    unittest.main()
