#!/usr/bin/env python3
"""
ULTRON Project AI Tool
Advanced AI-powered project management and file operations
"""

import os
import json
import requests
from pathlib import Path
from utils.ultron_logger import log_info, log_error
from tools.base import Tool

class UltronProjectTool(Tool):
    name = "ultron_project"
    description = "AI-powered project management with file operations and automation"
    
    def __init__(self, config):
        self.config = config
        self.project_root = Path.cwd()
        
    def match(self, command: str) -> bool:
        keywords = [
            "project", "file", "analyze", "review", "automate", 
            "maintain", "optimize", "refactor", "test", "deploy"
        ]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        try:
            if "analyze project" in command.lower():
                return self.analyze_project()
            elif "review file" in command.lower():
                return self.review_file(kwargs.get("file_path", ""))
            elif "optimize code" in command.lower():
                return self.optimize_code(kwargs.get("file_path", ""))
            elif "run tests" in command.lower():
                return self.run_tests()
            elif "update dependencies" in command.lower():
                return self.update_dependencies()
            elif "git status" in command.lower():
                return self.git_status()
            elif "create file" in command.lower():
                return self.create_file(kwargs.get("file_path", ""), kwargs.get("content", ""))
            elif "read file" in command.lower():
                return self.read_file(kwargs.get("file_path", ""))
            elif "write file" in command.lower():
                return self.write_file(kwargs.get("file_path", ""), kwargs.get("content", ""))
            else:
                return self.general_project_help(command)
                
        except Exception as e:
            log_error("ultron_project", f"Error: {str(e)}")
            return f"Error: {str(e)}"
    
    def analyze_project(self) -> str:
        """Comprehensive AI-powered project analysis"""
        log_info("ultron_project", "Running project analysis")
        
        # Collect project metrics
        py_files = list(self.project_root.rglob("*.py"))
        total_lines = sum(len(open(f, 'r').readlines()) for f in py_files if f.is_file())
        
        # Create analysis prompt
        analysis_data = {
            "python_files": len(py_files),
            "total_lines": total_lines,
            "key_files": [str(f) for f in py_files if f.name in ["main.py", "agent_core.py", "brain.py"]],
            "config_files": [str(f) for f in self.project_root.glob("*.json")],
            "has_tests": bool(list(self.project_root.glob("test*.py")))
        }
        
        prompt = f"""
        Analyze this ULTRON Agent project:
        
        Project Structure:
        - Python files: {analysis_data['python_files']}
        - Total lines of code: {analysis_data['total_lines']}
        - Key files: {', '.join(analysis_data['key_files'])}
        - Config files: {', '.join(analysis_data['config_files'])}
        - Has tests: {analysis_data['has_tests']}
        
        Provide analysis on:
        1. Code organization and architecture
        2. Potential improvements
        3. Security considerations
        4. Performance optimizations
        5. Maintenance recommendations
        """
        
        analysis = self.call_ai(prompt)
        
        # Save analysis
        with open("project_analysis.md", "w") as f:
            f.write(f"# ULTRON Project Analysis\n\n{analysis}")
        
        return f"Project analysis complete. Saved to project_analysis.md\n\n{analysis[:500]}..."
    
    def review_file(self, file_path: str) -> str:
        """AI-powered code review"""
        if not file_path:
            return "Please specify a file path for review"
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            prompt = f"""
            Review this Python code for the ULTRON Agent project:
            
            File: {file_path}
            
            Code:
            {content[:2000]}...
            
            Provide feedback on:
            1. Code quality and style
            2. Potential bugs or issues
            3. Performance improvements
            4. Security vulnerabilities
            5. Best practices compliance
            """
            
            review = self.call_ai(prompt)
            
            # Save review
            review_file = f"review_{Path(file_path).stem}.md"
            with open(review_file, "w") as f:
                f.write(f"# Code Review: {file_path}\n\n{review}")
            
            return f"Code review complete. Saved to {review_file}\n\n{review[:300]}..."
            
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    def optimize_code(self, file_path: str) -> str:
        """AI-powered code optimization suggestions"""
        if not file_path:
            return "Please specify a file path for optimization"
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            prompt = f"""
            Optimize this Python code for the ULTRON Agent project:
            
            File: {file_path}
            
            Current code:
            {content[:1500]}...
            
            Provide specific optimization suggestions for:
            1. Performance improvements
            2. Memory usage reduction
            3. Code simplification
            4. Better error handling
            5. Async/await optimizations
            
            Include code examples where possible.
            """
            
            optimization = self.call_ai(prompt)
            
            # Save optimization suggestions
            opt_file = f"optimization_{Path(file_path).stem}.md"
            with open(opt_file, "w") as f:
                f.write(f"# Code Optimization: {file_path}\n\n{optimization}")
            
            return f"Optimization suggestions saved to {opt_file}\n\n{optimization[:300]}..."
            
        except Exception as e:
            return f"Error optimizing file {file_path}: {str(e)}"
    
    def run_tests(self) -> str:
        """Run project tests with AI analysis"""
        import subprocess
        
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "-v"],
                capture_output=True, text=True, timeout=60
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode != 0:
                # Ask AI to analyze test failures
                prompt = f"""
                Analyze these test failures for the ULTRON Agent project:
                
                Test output:
                {output[:1000]}...
                
                Provide:
                1. Root cause analysis
                2. Suggested fixes
                3. Prevention strategies
                """
                
                analysis = self.call_ai(prompt)
                
                with open("test_failure_analysis.md", "w") as f:
                    f.write(f"# Test Failure Analysis\n\n{analysis}")
                
                return f"Tests failed. Analysis saved to test_failure_analysis.md\n\n{output[:500]}..."
            else:
                return f"All tests passed!\n\n{output[:300]}..."
                
        except subprocess.TimeoutExpired:
            return "Tests timed out after 60 seconds"
        except Exception as e:
            return f"Error running tests: {str(e)}"
    
    def update_dependencies(self) -> str:
        """Check and suggest dependency updates"""
        import subprocess
        
        try:
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout) if result.stdout else []
                
                if outdated:
                    prompt = f"""
                    Review these dependency updates for the ULTRON Agent project:
                    
                    Outdated packages:
                    {json.dumps(outdated, indent=2)}
                    
                    Recommend which updates are:
                    1. Safe to apply immediately
                    2. Require testing
                    3. May have breaking changes
                    4. Should be avoided
                    """
                    
                    recommendations = self.call_ai(prompt)
                    
                    with open("dependency_recommendations.md", "w") as f:
                        f.write(f"# Dependency Update Recommendations\n\n{recommendations}")
                    
                    return f"Found {len(outdated)} outdated packages. Recommendations saved to dependency_recommendations.md"
                else:
                    return "All dependencies are up to date!"
            else:
                return f"Error checking dependencies: {result.stderr}"
                
        except Exception as e:
            return f"Error updating dependencies: {str(e)}"
    
    def git_status(self) -> str:
        """Get git status with AI insights"""
        import subprocess
        
        try:
            status = subprocess.getoutput("git status --porcelain")
            branch = subprocess.getoutput("git branch --show-current")
            last_commit = subprocess.getoutput("git log -1 --format='%h %s (%cr)'")
            
            if status:
                prompt = f"""
                Analyze this git status for the ULTRON Agent project:
                
                Branch: {branch}
                Last commit: {last_commit}
                
                Changes:
                {status}
                
                Provide insights on:
                1. What changes were made
                2. Suggested commit message
                3. Files that should be reviewed
                4. Potential issues
                """
                
                insights = self.call_ai(prompt)
                
                return f"Git Status:\nBranch: {branch}\nLast commit: {last_commit}\n\nChanges:\n{status}\n\nAI Insights:\n{insights[:400]}..."
            else:
                return f"Git Status: Clean\nBranch: {branch}\nLast commit: {last_commit}"
                
        except Exception as e:
            return f"Error getting git status: {str(e)}"
    
    def create_file(self, file_path: str, content: str) -> str:
        """Create a new file with AI-generated content if needed"""
        if not file_path:
            return "Please specify a file path"
        
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if not content:
                # Ask AI to generate appropriate content based on file type
                prompt = f"""
                Generate appropriate content for this file in the ULTRON Agent project:
                
                File path: {file_path}
                File type: {path.suffix}
                
                Create professional, well-documented code or content suitable for this file.
                """
                
                content = self.call_ai(prompt)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            log_info("ultron_project", f"Created file: {file_path}")
            return f"File created: {file_path}\n\nContent preview:\n{content[:200]}..."
            
        except Exception as e:
            return f"Error creating file {file_path}: {str(e)}"
    
    def read_file(self, file_path: str) -> str:
        """Read file with AI summary"""
        if not file_path:
            return "Please specify a file path"
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Provide AI summary for large files
            if len(content) > 1000:
                prompt = f"""
                Summarize this file from the ULTRON Agent project:
                
                File: {file_path}
                Content: {content[:1500]}...
                
                Provide:
                1. Purpose and functionality
                2. Key components
                3. Dependencies
                4. Important notes
                """
                
                summary = self.call_ai(prompt)
                return f"File: {file_path}\n\nAI Summary:\n{summary}\n\nFull content:\n{content[:500]}..."
            else:
                return f"File: {file_path}\n\nContent:\n{content}"
                
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    def write_file(self, file_path: str, content: str) -> str:
        """Write file with AI validation"""
        if not file_path or not content:
            return "Please specify both file path and content"
        
        try:
            # Ask AI to validate content before writing
            prompt = f"""
            Validate this content for the ULTRON Agent project file:
            
            File: {file_path}
            Content: {content[:1000]}...
            
            Check for:
            1. Syntax errors (if code)
            2. Security issues
            3. Best practices compliance
            4. Compatibility with project
            
            Respond with "VALID" if okay, or list issues.
            """
            
            validation = self.call_ai(prompt)
            
            if "VALID" in validation.upper():
                with open(file_path, 'w') as f:
                    f.write(content)
                
                log_info("ultron_project", f"Updated file: {file_path}")
                return f"File updated: {file_path}\n\nValidation: {validation}"
            else:
                return f"Content validation failed:\n{validation}\n\nFile not updated."
                
        except Exception as e:
            return f"Error writing file {file_path}: {str(e)}"
    
    def general_project_help(self, command: str) -> str:
        """General AI assistance for project tasks"""
        prompt = f"""
        Help with this ULTRON Agent project task:
        
        Request: {command}
        
        Project context: This is an advanced AI agent platform with:
        - Multi-modal interfaces (voice, vision, GUI, API)
        - Tool ecosystem with 15+ built-in tools
        - OpenAI-compatible API endpoints
        - Real-time monitoring and state persistence
        
        Provide specific, actionable guidance.
        """
        
        help_response = self.call_ai(prompt)
        return f"ULTRON Project Assistant:\n\n{help_response}"
    
    def call_ai(self, prompt: str) -> str:
        """Call AI service for analysis"""
        try:
            # Try Claude first
            api_key = self.config.get("anthropic_api_key", "")
            if api_key:
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 2000,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json().get("content", [{}])[0].get("text", "No response")
            
            # Fallback to MiniMax
            api_key = self.config.get("minimax_api_key", "")
            if api_key:
                response = requests.post(
                    "https://api.minimax.io/v1/text/chatcompletion",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "abab6.5s-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
        
        except Exception as e:
            log_error("ultron_project", f"AI call failed: {str(e)}")
        
        return "AI service unavailable - check API configuration"
    
    @staticmethod
    def schema():
        return {
            "name": "ultron_project",
            "description": "AI-powered project management with file operations and automation",
            "parameters": {
                "command": {"type": "string", "description": "Project management command"},
                "file_path": {"type": "string", "description": "File path for operations"},
                "content": {"type": "string", "description": "File content for write operations"}
            }
        }