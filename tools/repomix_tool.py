"""
ULTRON Agent - Repomix Integration Tool

Provides advanced codebase analysis, packaging, and natural language search
capabilities for local and remote repositories using Repomix technology.

Key Features:
- Pack local codebases for AI analysis
- Fetch and analyze remote GitHub repositories
- Natural language search through code
- Partial content reading for large reports
- Dynamic report updates without restart
"""

import asyncio
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tools.tool_interface import ToolInterface
from utils.ultron_logger import (
    log_ai_decision, log_error, log_file_operation, log_info
)


class RepomixTool(ToolInterface):
    """
    Advanced codebase analysis tool using Repomix for AI-powered understanding.

    Capabilities:
    - Package codebases for LLM consumption
    - Natural language code search
    - Remote repository analysis
    - Real-time report generation
    - Context-aware code understanding
    """

    def __init__(self) -> None:
        self.output_dir: Path = Path("repomix_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.cache_dir: Path = Path("cache/repomix")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Registry of packed outputs for quick access
        self.output_registry: Dict[str, Dict[str, Any]] = {}

        log_info("repomix_tool", "Repomix integration initialized")
        self._check_dependencies()

    @property
    def name(self) -> str:
        return "Repomix Codebase Analyzer"

    @property
    def description(self) -> str:
        return (
            "Advanced codebase analysis with natural language search, "
            "repository packaging, and AI-powered code understanding"
        )

    def match(self, command: str) -> bool:
        """Check if command should trigger Repomix operations"""
        keywords: List[str] = [
            "repomix", "pack codebase", "analyze code", "code analysis",
            "repository analysis", "search codebase", "grep code",
            "package repository", "analyze repository", "code search",
            "find in codebase", "codebase overview", "project analysis"
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute Repomix operations"""
        log_info("repomix_tool", f"Executing command: {command}")

        try:
            cmd_lower: str = command.lower()

            # Pack local codebase
            if "pack" in cmd_lower and "local" in cmd_lower or (
                "package directory" in cmd_lower
            ):
                directory: str = (
                    kwargs.get("directory") or
                    self._extract_path(command)
                )
                return self._pack_local_codebase(directory)

            # Pack remote repository
            elif "pack" in cmd_lower and (
                "remote" in cmd_lower or "github" in cmd_lower or
                "repository" in cmd_lower
            ):
                repo_url: str = (
                    kwargs.get("repo_url") or self._extract_url(command)
                )
                return self._pack_remote_repository(repo_url)

            # Natural language search
            elif "search" in cmd_lower or "grep" in cmd_lower or (
                "find" in cmd_lower
            ):
                query: str = kwargs.get("query") or command
                output_id: Optional[str] = (
                    kwargs.get("output_id") or
                    self._get_latest_output_id()
                )
                return self._grep_repomix_output(query, output_id)

            # Read partial content
            elif "read" in cmd_lower and (
                "lines" in cmd_lower or "partial" in cmd_lower
            ):
                output_id = (
                    kwargs.get("output_id") or
                    self._get_latest_output_id()
                )
                start_line: int = kwargs.get("start_line", 1)
                end_line: int = kwargs.get("end_line", 100)
                return self._read_repomix_output(
                    output_id, start_line, end_line
                )

            # Attach new packed output
            elif "attach" in cmd_lower or "register" in cmd_lower:
                file_path: str = (
                    kwargs.get("file_path") or self._extract_path(command)
                )
                return self._attach_packed_output(file_path)

            # List available outputs
            elif "list" in cmd_lower or "show" in cmd_lower or (
                "status" in cmd_lower
            ):
                return self._list_outputs()

            # Get codebase overview
            elif "overview" in cmd_lower or "summary" in cmd_lower:
                output_id = (
                    kwargs.get("output_id") or
                    self._get_latest_output_id()
                )
                return self._generate_overview(output_id)

            else:
                return self._show_help()

        except Exception as e:
            log_error(
                "repomix_tool", f"Error executing command: {e}",
                exception=e
            )
            return f"❌ Repomix Error: {str(e)}"

    # ─────────────────────────────────────────────────────────────────────────
    # Core Repomix Operations
    # ─────────────────────────────────────────────────────────────────────────

    def _pack_local_codebase(self, directory: str) -> str:
        """
        Package a local code directory into a consolidated file for AI analysis.

        Args:
            directory: Path to the local codebase

        Returns:
            Status message with output file location and metrics
        """
        log_info("repomix_tool", f"Packing local codebase: {directory}")

        try:
            dir_path = Path(directory).resolve()
            if not dir_path.exists():
                return f"❌ Directory not found: {directory}"

            # Generate output filename
            output_id = self._generate_output_id(str(dir_path))
            output_file = self.output_dir / f"{output_id}.txt"

            # Collect codebase files
            files_data = self._collect_files(dir_path)

            # Generate repomix-style output
            content = self._format_repomix_output(
                project_name=dir_path.name,
                files=files_data,
                root_path=dir_path
            )

            # Write output
            output_file.write_text(content, encoding='utf-8')

            # Register output
            self._register_output(output_id, output_file, {
                "type": "local",
                "source": str(dir_path),
                "timestamp": datetime.now().isoformat(),
                "file_count": len(files_data),
                "total_lines": sum(f["lines"] for f in files_data)
            })

            log_file_operation("repomix_tool", f"Packed {len(files_data)} files", str(output_file), "created")

            return f"""✅ Codebase Packed Successfully

📦 **Output ID**: {output_id}
📁 **Location**: {output_file}
📊 **Metrics**:
   - Files analyzed: {len(files_data)}
   - Total lines: {sum(f['lines'] for f in files_data):,}
   - Project: {dir_path.name}

🔍 **Next Steps**:
   - Search code: "search for <query> in {output_id}"
   - Read content: "read lines 1-100 from {output_id}"
   - Get overview: "overview of {output_id}"
"""

        except Exception as e:
            log_error("repomix_tool", f"Error packing local codebase: {e}", exception=e)
            return f"❌ Error packing codebase: {str(e)}"

    def _pack_remote_repository(self, repo_url: str) -> str:
        """
        Fetch and package a remote GitHub repository for analysis.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Status message with output file location
        """
        log_info("repomix_tool", f"Packing remote repository: {repo_url}")

        try:
            # Extract owner and repo name
            match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
            if not match:
                return f"❌ Invalid GitHub URL: {repo_url}"

            owner, repo = match.groups()
            repo = repo.replace('.git', '')

            # Clone to temp directory
            temp_dir = self.cache_dir / f"{owner}_{repo}"

            if not temp_dir.exists():
                log_info("repomix_tool", f"Cloning repository: {repo_url}")
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", repo_url, str(temp_dir)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode != 0:
                    return f"❌ Git clone failed: {result.stderr}"

            # Pack the cloned repository
            return self._pack_local_codebase(str(temp_dir))

        except subprocess.TimeoutExpired:
            return f"❌ Repository clone timed out (5 min limit)"
        except Exception as e:
            log_error("repomix_tool", f"Error packing remote repository: {e}", exception=e)
            return f"❌ Error: {str(e)}"

    def _grep_repomix_output(self, query: str, output_id: str) -> str:
        """
        Search through Repomix output using natural language or regex.

        Args:
            query: Search query (natural language or regex pattern)
            output_id: ID of the output to search

        Returns:
            Formatted search results with file locations and context
        """
        log_ai_decision("repomix_tool", f"Searching for: {query}", ai_model="pattern_matching", confidence_score=0.9)

        try:
            if output_id not in self.output_registry:
                return f"❌ Output not found: {output_id}. Use 'list outputs' to see available outputs."

            output_file = Path(self.output_registry[output_id]["file_path"])
            content = output_file.read_text(encoding='utf-8')

            # Extract search terms
            search_terms = self._extract_search_terms(query)

            # Find matches
            matches = []
            lines = content.split('\n')

            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                if any(term in line_lower for term in search_terms):
                    # Get context (3 lines before and after)
                    context_start = max(0, i - 4)
                    context_end = min(len(lines), i + 3)
                    context = lines[context_start:context_end]

                    matches.append({
                        "line_number": i,
                        "content": line.strip(),
                        "context": context
                    })

            if not matches:
                return f"ℹ️ No matches found for '{query}' in {output_id}"

            # Limit results
            matches = matches[:20]  # Top 20 results

            result = f"🔍 **Search Results for '{query}'**\n"
            result += f"📦 Output: {output_id}\n"
            result += f"✅ Found {len(matches)} matches\n\n"

            for match in matches:
                result += f"**Line {match['line_number']}**:\n"
                result += f"```\n{match['content']}\n```\n\n"

            return result

        except Exception as e:
            log_error("repomix_tool", f"Error searching output: {e}", exception=e)
            return f"❌ Search error: {str(e)}"

    def _read_repomix_output(self, output_id: str, start_line: int, end_line: int) -> str:
        """
        Read partial content from a Repomix output file.

        Args:
            output_id: ID of the output to read
            start_line: Starting line number
            end_line: Ending line number

        Returns:
            Content of specified lines
        """
        log_info("repomix_tool", f"Reading lines {start_line}-{end_line} from {output_id}")

        try:
            if output_id not in self.output_registry:
                return f"❌ Output not found: {output_id}"

            output_file = Path(self.output_registry[output_id]["file_path"])
            lines = output_file.read_text(encoding='utf-8').split('\n')

            # Validate line numbers
            if start_line < 1:
                start_line = 1
            if end_line > len(lines):
                end_line = len(lines)
            if start_line > end_line:
                return f"❌ Invalid line range: {start_line}-{end_line}"

            # Extract lines
            content_lines = lines[start_line-1:end_line]

            result = f"📄 **Content from {output_id}** (Lines {start_line}-{end_line})\n\n"
            result += "```\n"
            for i, line in enumerate(content_lines, start_line):
                result += f"{i:5d} | {line}\n"
            result += "```\n"

            return result

        except Exception as e:
            log_error("repomix_tool", f"Error reading output: {e}", exception=e)
            return f"❌ Read error: {str(e)}"

    def _attach_packed_output(self, file_path: str) -> str:
        """
        Attach a new packed output for AI analysis without restart.

        Args:
            file_path: Path to the packed output file

        Returns:
            Confirmation message with output ID
        """
        log_info("repomix_tool", f"Attaching output: {file_path}")

        try:
            file_path_obj = Path(file_path).resolve()
            if not file_path_obj.exists():
                return f"❌ File not found: {file_path}"

            # Generate output ID from file content
            content = file_path_obj.read_text(encoding='utf-8')
            output_id = hashlib.md5(file_path.encode()).hexdigest()[:12]

            # Register output
            self._register_output(output_id, file_path_obj, {
                "type": "attached",
                "source": str(file_path_obj),
                "timestamp": datetime.now().isoformat(),
                "size_kb": file_path_obj.stat().st_size / 1024
            })

            log_file_operation("repomix_tool", "Attached packed output", str(file_path_obj), "registered")

            return f"""✅ Output Attached Successfully

📦 **Output ID**: {output_id}
📁 **File**: {file_path_obj.name}
💾 **Size**: {file_path_obj.stat().st_size / 1024:.2f} KB

🔍 **Usage**:
   - Search: "search for <query> in {output_id}"
   - Read: "read lines 1-100 from {output_id}"
"""

        except Exception as e:
            log_error("repomix_tool", f"Error attaching output: {e}", exception=e)
            return f"❌ Attach error: {str(e)}"

    def _list_outputs(self) -> str:
        """List all available Repomix outputs"""
        if not self.output_registry:
            return "ℹ️ No packed outputs available. Use 'pack codebase' to create one."

        result = "📦 **Available Repomix Outputs**\n\n"

        for output_id, metadata in self.output_registry.items():
            result += f"**{output_id}**\n"
            result += f"   📁 Source: {metadata.get('source', 'Unknown')}\n"
            result += f"   📅 Created: {metadata.get('timestamp', 'Unknown')}\n"

            if 'file_count' in metadata:
                result += f"   📊 Files: {metadata['file_count']}\n"
            if 'total_lines' in metadata:
                result += f"   📝 Lines: {metadata['total_lines']:,}\n"

            result += "\n"

        return result

    def _generate_overview(self, output_id: str) -> str:
        """Generate codebase overview from packed output"""
        try:
            if output_id not in self.output_registry:
                return f"❌ Output not found: {output_id}"

            metadata = self.output_registry[output_id]

            overview = f"""📊 **Codebase Overview: {output_id}**

**Source**: {metadata.get('source', 'Unknown')}
**Type**: {metadata.get('type', 'Unknown')}
**Created**: {metadata.get('timestamp', 'Unknown')}

**Metrics**:
   - Files: {metadata.get('file_count', 'N/A')}
   - Total Lines: {metadata.get('total_lines', 'N/A')}
   - Size: {metadata.get('size_kb', 'N/A')} KB

**Available Operations**:
   - Search: "search for <pattern> in {output_id}"
   - Read: "read lines 1-100 from {output_id}"
   - Full analysis: Use packed output with LLM
"""

            return overview

        except Exception as e:
            return f"❌ Error generating overview: {str(e)}"

    # ─────────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _collect_files(self, root_path: Path) -> List[Dict]:
        """Collect all relevant files from directory"""
        files_data = []

        # File extensions to include
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.json', '.yaml', '.yml', '.md', '.txt',
            '.sh', '.bat', '.ps1', '.sql', '.r', '.m', '.f90'
        }

        # Directories to skip
        skip_dirs = {
            '__pycache__', '.git', 'node_modules', '.pytest_cache',
            'venv', '.venv', 'env', 'dist', 'build', '.next',
            'coverage', '.coverage', 'htmlcov', 'logs'
        }

        for file_path in root_path.rglob('*'):
            # Skip if in excluded directory
            if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                continue

            # Only process files with relevant extensions
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.count('\n') + 1

                    files_data.append({
                        "path": str(file_path.relative_to(root_path)),
                        "content": content,
                        "lines": lines,
                        "extension": file_path.suffix
                    })
                except Exception as e:
                    log_error("repomix_tool", f"Error reading {file_path}: {e}")
                    continue

        return files_data

    def _format_repomix_output(self, project_name: str, files: List[Dict], root_path: Path) -> str:
        """Format collected files into Repomix-style output"""
        output = []

        # Header
        output.append(f"# Repomix Output - {project_name}")
        output.append(f"Generated: {datetime.now().isoformat()}")
        output.append(f"Files: {len(files)}")
        output.append(f"Total Lines: {sum(f['lines'] for f in files):,}")
        output.append("\n" + "="*80 + "\n")

        # File tree
        output.append("## File Tree\n")
        for file_data in sorted(files, key=lambda x: x['path']):
            output.append(f"├── {file_data['path']} ({file_data['lines']} lines)")
        output.append("\n" + "="*80 + "\n")

        # File contents
        output.append("## File Contents\n")
        for file_data in sorted(files, key=lambda x: x['path']):
            output.append(f"\n### {file_data['path']}\n")
            output.append(f"```{file_data['extension'][1:]}\n")
            output.append(file_data['content'])
            output.append("\n```\n")

        return '\n'.join(output)

    def _register_output(self, output_id: str, file_path: Path, metadata: Dict):
        """Register a packed output in the registry"""
        self.output_registry[output_id] = {
            "file_path": str(file_path),
            **metadata
        }

        # Save registry to disk
        registry_file = self.output_dir / "registry.json"
        registry_file.write_text(json.dumps(self.output_registry, indent=2))

    def _generate_output_id(self, source: str) -> str:
        """Generate unique output ID from source"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_hash = hashlib.md5(source.encode()).hexdigest()[:8]
        return f"{timestamp}_{source_hash}"

    def _get_latest_output_id(self) -> Optional[str]:
        """Get the most recently created output ID"""
        if not self.output_registry:
            return None

        sorted_ids = sorted(
            self.output_registry.items(),
            key=lambda x: x[1].get('timestamp', ''),
            reverse=True
        )

        return sorted_ids[0][0] if sorted_ids else None

    def _extract_path(self, command: str) -> str:
        """Extract file path from command"""
        # Look for quoted paths
        match = re.search(r'["\']([^"\']+)["\']', command)
        if match:
            return match.group(1)

        # Look for common path patterns
        words = command.split()
        for word in words:
            if '/' in word or '\\' in word:
                return word

        # Default to current directory
        return "."

    def _extract_url(self, command: str) -> str:
        """Extract URL from command"""
        match = re.search(r'https?://[^\s]+', command)
        return match.group(0) if match else ""

    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from natural language query"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or'}

        terms = re.findall(r'\b\w+\b', query.lower())
        return [term for term in terms if term not in stop_words and len(term) > 2]

    def _check_dependencies(self):
        """Check if git is available"""
        try:
            subprocess.run(['git', '--version'], capture_output=True, timeout=5)
            log_info("repomix_tool", "Git dependency verified")
        except Exception:
            log_error("repomix_tool", "Git not found - remote repository features unavailable")

    def _show_help(self) -> str:
        """Show help message"""
        return """🔍 **Repomix Tool - Advanced Codebase Analysis**

**Available Commands**:

📦 **Pack Codebase**:
   - "pack local codebase /path/to/project"
   - "pack remote repository https://github.com/owner/repo"

🔎 **Search Code**:
   - "search for <query> in <output_id>"
   - "grep <pattern> in codebase"
   - "find error handling in codebase"

📄 **Read Content**:
   - "read lines 1-100 from <output_id>"
   - "read partial content from <output_id>"

📊 **Manage Outputs**:
   - "list outputs" - Show all available outputs
   - "overview of <output_id>" - Get codebase summary
   - "attach output /path/to/file" - Register existing output

**Examples**:
   - "pack local codebase C:/Projects/ultron_agent"
   - "search for authentication logic in codebase"
   - "read lines 1-50 from 20250128_abc123"
"""

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return tool schema for API documentation"""
        return {
            "name": "repomix_tool",
            "description": (
                "Advanced codebase analysis with natural language "
                "search and repository packaging"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The Repomix command to execute"
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directory path for local packing"
                    },
                    "repo_url": {
                        "type": "string",
                        "description": (
                            "GitHub repository URL for remote packing"
                        )
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query for grep operations"
                    },
                    "output_id": {
                        "type": "string",
                        "description": (
                            "ID of the packed output to operate on"
                        )
                    },
                    "start_line": {
                        "type": "integer",
                        "description": (
                            "Starting line number for partial read"
                        )
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Ending line number for partial read"
                    }
                },
                "required": ["command"]
            }
        }


# Export the tool for auto-discovery
def get_tool() -> RepomixTool:
    """Required function for tool loader"""
    return RepomixTool()

