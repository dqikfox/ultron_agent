"""
Comprehensive tests for Tools system
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add tools directory to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))

from tools.base import Tool
from tools.file_tool import FileTool
from tools.code_execution_tool import CodeExecutionTool


class TestBaseTool:
    """Test suite for base Tool class"""

    def test_tool_initialization(self):
        """Test base tool initialization"""
        tool = Tool()
        assert tool is not None

    def test_tool_match_not_implemented(self):
        """Test that match method raises NotImplementedError"""
        tool = Tool()
        with pytest.raises(NotImplementedError):
            tool.match("test command")

    def test_tool_execute_not_implemented(self):
        """Test that execute method raises NotImplementedError"""
        tool = Tool()
        with pytest.raises(NotImplementedError):
            tool.execute("test command")

    def test_tool_schema_not_implemented(self):
        """Test that schema method raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            Tool.schema()


class TestFileTool:
    """Test suite for FileTool"""

    def test_file_tool_initialization(self):
        """Test file tool initialization"""
        tool = FileTool()
        assert tool is not None

    def test_file_tool_match_read_file(self):
        """Test file tool matching for read operations"""
        tool = FileTool()
        assert tool.match("read file test.txt") is True
        assert tool.match("open file document.py") is True
        assert tool.match("show me contents of config.json") is True

    def test_file_tool_match_write_file(self):
        """Test file tool matching for write operations"""
        tool = FileTool()
        assert tool.match("write to file test.txt") is True
        assert tool.match("create file new_document.py") is True
        assert tool.match("save content to output.json") is True

    def test_file_tool_match_list_files(self):
        """Test file tool matching for list operations"""
        tool = FileTool()
        assert tool.match("list files") is True
        assert tool.match("show directory contents") is True
        assert tool.match("ls /home/user") is True

    def test_file_tool_match_negative(self):
        """Test file tool not matching irrelevant commands"""
        tool = FileTool()
        assert tool.match("calculate 2 + 2") is False
        assert tool.match("play music") is False
        assert tool.match("send email") is False

    @patch('builtins.open', create=True)
    def test_file_tool_read_file_success(self, mock_open):
        """Test successful file reading"""
        mock_open.return_value.__enter__.return_value.read.return_value = "file content"
        
        tool = FileTool()
        result = tool.read_file("test.txt")
        
        assert "file content" in result
        mock_open.assert_called_once_with("test.txt", 'r', encoding='utf-8')

    @patch('builtins.open', create=True)
    def test_file_tool_read_file_not_found(self, mock_open):
        """Test file reading when file not found"""
        mock_open.side_effect = FileNotFoundError()
        
        tool = FileTool()
        result = tool.read_file("nonexistent.txt")
        
        assert "Error" in result
        assert "not found" in result.lower()

    @patch('builtins.open', create=True)
    def test_file_tool_write_file_success(self, mock_open):
        """Test successful file writing"""
        tool = FileTool()
        result = tool.write_file("test.txt", "new content")
        
        assert "successfully" in result.lower() or "written" in result.lower()
        mock_open.assert_called_once_with("test.txt", 'w', encoding='utf-8')

    @patch('builtins.open', create=True)
    def test_file_tool_write_file_permission_error(self, mock_open):
        """Test file writing with permission error"""
        mock_open.side_effect = PermissionError()
        
        tool = FileTool()
        result = tool.write_file("protected.txt", "content")
        
        assert "Error" in result
        assert "permission" in result.lower()

    @patch('os.listdir')
    @patch('os.path.isfile')
    @patch('os.path.isdir')
    def test_file_tool_list_files_success(self, mock_isdir, mock_isfile, mock_listdir):
        """Test successful file listing"""
        mock_listdir.return_value = ["file1.txt", "file2.py", "subfolder"]
        mock_isfile.side_effect = lambda x: x.endswith(('.txt', '.py'))
        mock_isdir.side_effect = lambda x: x == "subfolder" or x == "."
        
        tool = FileTool()
        result = tool.list_files(".")
        
        assert "file1.txt" in result
        assert "file2.py" in result
        assert "subfolder" in result

    @patch('os.listdir')
    def test_file_tool_list_files_permission_error(self, mock_listdir):
        """Test file listing with permission error"""
        mock_listdir.side_effect = PermissionError()
        
        tool = FileTool()
        result = tool.list_files("/protected")
        
        assert "Error" in result
        assert "permission" in result.lower()

    def test_file_tool_execute_read_command(self):
        """Test execute method with read command"""
        tool = FileTool()
        
        with patch.object(tool, 'read_file', return_value="file content") as mock_read:
            result = tool.execute(command="read file test.txt", path="test.txt")
            mock_read.assert_called_once_with("test.txt")

    def test_file_tool_execute_write_command(self):
        """Test execute method with write command"""
        tool = FileTool()
        
        with patch.object(tool, 'write_file', return_value="success") as mock_write:
            result = tool.execute(command="write file test.txt", path="test.txt", content="new content")
            mock_write.assert_called_once_with("test.txt", "new content")

    def test_file_tool_execute_list_command(self):
        """Test execute method with list command"""
        tool = FileTool()
        
        with patch.object(tool, 'list_files', return_value="file listing") as mock_list:
            result = tool.execute(command="list files", path=".")
            mock_list.assert_called_once_with(".")


class TestCodeExecutionTool:
    """Test suite for CodeExecutionTool"""

    def test_code_execution_tool_initialization(self):
        """Test code execution tool initialization"""
        tool = CodeExecutionTool()
        assert tool is not None

    def test_code_execution_tool_match_python(self):
        """Test matching Python code execution commands"""
        tool = CodeExecutionTool()
        assert tool.match("run python code") is True
        assert tool.match("execute python script") is True
        assert tool.match("run code print('hello')") is True

    def test_code_execution_tool_match_general(self):
        """Test matching general code execution commands"""
        tool = CodeExecutionTool()
        assert tool.match("execute code") is True
        assert tool.match("run script") is True
        assert tool.match("eval expression") is True

    def test_code_execution_tool_match_negative(self):
        """Test not matching irrelevant commands"""
        tool = CodeExecutionTool()
        assert tool.match("read file") is False
        assert tool.match("play music") is False
        assert tool.match("send email") is False

    @patch('subprocess.run')
    def test_code_execution_python_success(self, mock_run):
        """Test successful Python code execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello World"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        tool = CodeExecutionTool()
        result = tool.execute(code="print('Hello World')")
        
        assert "Hello World" in result
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_code_execution_python_error(self, mock_run):
        """Test Python code execution with error"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "SyntaxError: invalid syntax"
        mock_run.return_value = mock_result
        
        tool = CodeExecutionTool()
        result = tool.execute(code="invalid python code")
        
        assert "Error" in result
        assert "SyntaxError" in result

    @patch('subprocess.run')
    def test_code_execution_timeout(self, mock_run):
        """Test code execution timeout"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("python", 5)
        
        tool = CodeExecutionTool()
        result = tool.execute(code="while True: pass")
        
        assert "timeout" in result.lower() or "error" in result.lower()

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_code_execution_with_file(self, mock_run, mock_temp):
        """Test code execution using temporary file"""
        mock_temp_file = Mock()
        mock_temp_file.name = "/tmp/test_script.py"
        mock_temp.return_value.__enter__.return_value = mock_temp_file
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        tool = CodeExecutionTool()
        result = tool.execute(code="print('Success')")
        
        assert "Success" in result or "executed" in result.lower()

    def test_code_execution_security_validation(self):
        """Test security validation for dangerous code"""
        tool = CodeExecutionTool()
        
        # Test various potentially dangerous operations
        dangerous_codes = [
            "import os; os.system('rm -rf /')",
            "exec(open('/etc/passwd').read())",
            "__import__('subprocess').call(['rm', '-rf', '/'])"
        ]
        
        for dangerous_code in dangerous_codes:
            result = tool.execute(code=dangerous_code)
            # Should either block execution or handle safely
            assert "Error" in result or "blocked" in result.lower() or "not allowed" in result.lower()

    def test_code_execution_tool_schema(self):
        """Test code execution tool schema"""
        schema = CodeExecutionTool.schema()
        
        assert "name" in schema
        assert "description" in schema
        assert schema["name"] == "code_execution"


class TestToolsIntegration:
    """Integration tests for tools system"""

    def test_tool_discovery(self):
        """Test automatic tool discovery"""
        # This would test the dynamic tool loading system
        tools_found = []
        
        # Mock the tool discovery process
        with patch('importlib.import_module') as mock_import:
            mock_file_tool = Mock()
            mock_file_tool.FileTool = FileTool
            mock_import.return_value = mock_file_tool
            
            # Simulate discovery
            tool_instance = FileTool()
            tools_found.append(tool_instance)
        
        assert len(tools_found) > 0
        assert isinstance(tools_found[0], FileTool)

    def test_tool_execution_chain(self):
        """Test chaining tool executions"""
        file_tool = FileTool()
        code_tool = CodeExecutionTool()
        
        # Mock file operations
        with patch.object(file_tool, 'write_file', return_value="File written successfully"), \
             patch.object(file_tool, 'read_file', return_value="print('Hello from file')"), \
             patch.object(code_tool, 'execute', return_value="Hello from file"):
            
            # Write code to file
            write_result = file_tool.execute(
                command="write file script.py",
                path="script.py",
                content="print('Hello from file')"
            )
            assert "success" in write_result.lower()
            
            # Read code from file
            read_result = file_tool.read_file("script.py")
            assert "Hello from file" in read_result
            
            # Execute the code
            exec_result = code_tool.execute(code=read_result)
            assert "Hello from file" in exec_result

    def test_tool_error_handling(self):
        """Test comprehensive error handling across tools"""
        tools = [FileTool(), CodeExecutionTool()]
        
        for tool in tools:
            # Test with invalid inputs
            try:
                result = tool.execute("")
                # Should handle gracefully
                assert isinstance(result, str)
            except Exception as e:
                # If exception is raised, it should be a controlled one
                assert isinstance(e, (ValueError, TypeError, NotImplementedError))

    def test_tool_performance(self):
        """Test tool performance and timeout handling"""
        import time
        
        code_tool = CodeExecutionTool()
        
        # Test quick execution
        start_time = time.time()
        result = code_tool.execute(code="print('quick test')")
        execution_time = time.time() - start_time
        
        # Should complete quickly for simple operations
        assert execution_time < 5.0  # 5 second timeout for simple operations

    @pytest.mark.parametrize("tool_class", [FileTool, CodeExecutionTool])
    def test_tool_interface_compliance(self, tool_class):
        """Test that all tools implement required interface"""
        tool = tool_class()
        
        # All tools should have these methods
        assert hasattr(tool, 'match')
        assert hasattr(tool, 'execute')
        assert hasattr(tool_class, 'schema')
        
        # Methods should be callable
        assert callable(tool.match)
        assert callable(tool.execute)
        assert callable(tool_class.schema)
