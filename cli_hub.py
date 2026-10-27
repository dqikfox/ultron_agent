#!/usr/bin/env python3
"""
ULTRON CLI Integration Hub v5.0
Integrates NVIDIA, GitHub, Hugging Face, Ollama, Docker, OpenAI
Into the existing ULTRON 3.0 Python system
"""

import asyncio
import subprocess
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import sqlite3
from pathlib import Path

@dataclass
class CLICommand:
    """CLI command definition"""
    name: str
    check_cmd: str
    exec_cmds: Dict[str, str]
    available: bool = False
    version: str = ""

class CLIIntegrationHub:
    """
    Central hub for all CLI tool integrations
    Provides unified interface to external tools
    """
    
    def __init__(self, db_path: Path = Path(".ultron/cli_history.db")):
        self.db_path = db_path
        self.tools: Dict[str, CLICommand] = {}
        self.execution_log: List[Dict] = []
        self._init_tools()
        self._init_db()
    
    def _init_db(self):
        """Initialize execution history database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cli_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool TEXT,
                    command TEXT,
                    success BOOLEAN,
                    output TEXT,
                    duration_ms INTEGER,
                    timestamp TIMESTAMP
                )
            """)
    
    def _init_tools(self):
        """Initialize all CLI tool definitions"""
        
        # NVIDIA GPU tools
        self.tools['nvidia'] = CLICommand(
            name='nvidia',
            check_cmd='nvidia-smi --version',
            exec_cmds={
                'status': 'nvidia-smi --query-gpu=name,memory.total,memory.used,temperature.gpu,utilization.gpu --format=csv,noheader',
                'processes': 'nvidia-smi pmon -c 1',
                'top': 'nvidia-smi --query-compute-apps=pid,name,used_memory --format=csv'
            }
        )
        
        # GitHub CLI
        self.tools['gh'] = CLICommand(
            name='gh',
            check_cmd='gh --version',
            exec_cmds={
                'auth_status': 'gh auth status',
                'repo_list': 'gh repo list --limit 100 --json name,description,url,stargazersCount',
                'issue_list': 'gh issue list --state open --json number,title,url,createdAt',
                'pr_list': 'gh pr list --state open --json number,title,url,author',
                'workflow_list': 'gh run list --limit 20 --json name,status,conclusion,createdAt'
            }
        )
        
        # Hugging Face CLI
        self.tools['hf'] = CLICommand(
            name='hf',
            check_cmd='huggingface-cli --version',
            exec_cmds={
                'whoami': 'huggingface-cli whoami',
                'repo_list': 'huggingface-cli repo list',
                'scan_cache': 'huggingface-cli scan-cache'
            }
        )
        
        # Ollama
        self.tools['ollama'] = CLICommand(
            name='ollama',
            check_cmd='ollama --version',
            exec_cmds={
                'list': 'ollama list',
                'ps': 'ollama ps',
                'version': 'ollama -v'
            }
        )
        
        # Docker
        self.tools['docker'] = CLICommand(
            name='docker',
            check_cmd='docker --version',
            exec_cmds={
                'ps': 'docker ps --format "{{json .}}"',
                'images': 'docker images --format "{{json .}}"',
                'stats': 'docker stats --no-stream --format "{{json .}}"',
                'info': 'docker info --format "{{json .}}"'
            }
        )
        
        # Python with AI libraries
        self.tools['python'] = CLICommand(
            name='python',
            check_cmd='python --version',
            exec_cmds={
                'gpu_check': 'python -c "import torch; print(torch.cuda.is_available())"',
                'transformers_version': 'python -c "import transformers; print(transformers.__version__)"'
            }
        )
        
        # Node/npm
        self.tools['npm'] = CLICommand(
            name='npm',
            check_cmd='npm --version',
            exec_cmds={
                'list': 'npm list --json --depth=0',
                'audit': 'npm audit --json'
            }
        )
        
        # Git
        self.tools['git'] = CLICommand(
            name='git',
            check_cmd='git --version',
            exec_cmds={
                'status': 'git status --porcelain',
                'log': 'git log --oneline -20',
                'branch': 'git branch -a'
            }
        )
    
    async def check_availability(self) -> List[str]:
        """Check which tools are available"""
        print("[CLI Hub] Probing tool availability...")
        available = []
        
        for name, tool in self.tools.items():
            try:
                result = await self._run_cmd(tool.check_cmd, timeout=5)
                tool.available = result['success']
                if result['success']:
                    tool.version = result['stdout'].split('\n')[0][:50]
                    available.append(name)
                    print(f"  ✓ {name}: {tool.version}")
            except Exception as e:
                tool.available = False
        
        print(f"[CLI Hub] {len(available)}/{len(self.tools)} tools ready\n")
        return available
    
    async def _run_cmd(self, cmd: str, timeout: int = 30) -> Dict:
        """Execute shell command"""
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
            
            return {
                'success': proc.returncode == 0,
                'stdout': stdout.decode('utf-8', errors='ignore'),
                'stderr': stderr.decode('utf-8', errors='ignore') if stderr else None
            }
        except asyncio.TimeoutError:
            return {'success': False, 'error': 'Timeout', 'stdout': '', 'stderr': ''}
        except Exception as e:
            return {'success': False, 'error': str(e), 'stdout': '', 'stderr': ''}
    
    async def execute(self, tool_name: str, command: str, args: List[str] = None) -> Dict:
        """Execute a CLI command"""
        tool = self.tools.get(tool_name)
        if not tool:
            return {'success': False, 'error': f'Tool {tool_name} not found'}
        
        if not tool.available:
            return {'success': False, 'error': f'Tool {tool_name} not available'}
        
        cmd_template = tool.exec_cmds.get(command)
        if not cmd_template:
            return {'success': False, 'error': f'Command {command} not found'}
        
        # Build command with args
        cmd = cmd_template
        if args:
            cmd = f"{cmd} {' '.join(args)}"
        
        start_time = datetime.now()
        result = await self._run_cmd(cmd)
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Log execution
        execution_record = {
            'tool': tool_name,
            'command': command,
            'success': result['success'],
            'output': result.get('stdout', '')[:500],
            'duration_ms': duration_ms,
            'timestamp': datetime.now()
        }
        
        self.execution_log.append(execution_record)
        self._persist_execution(execution_record)
        
        return result
    
    def _persist_execution(self, record: Dict):
        """Save execution to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO cli_executions (tool, command, success, output, duration_ms, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    record['tool'], record['command'], record['success'],
                    record['output'], record['duration_ms'], record['timestamp']
                ))
        except Exception as e:
            print(f"[CLI Hub] Failed to persist execution: {e}")
    
    async def ollama_generate(self, model: str, prompt: str) -> Dict:
        """Generate via Ollama API"""
        import aiohttp
        
        host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{host}/api/generate",
                    json={'model': model, 'prompt': prompt, 'stream': False}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {'success': True, 'response': data.get('response', '')}
                    else:
                        return {'success': False, 'error': f'HTTP {resp.status}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def ollama_embed(self, model: str, text: str) -> Dict:
        """Generate embeddings via Ollama"""
        import aiohttp
        
        host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{host}/api/embeddings",
                    json={'model': model, 'prompt': text}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {'success': True, 'embedding': data.get('embedding', [])}
                    else:
                        return {'success': False, 'error': f'HTTP {resp.status}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_capabilities(self) -> List[Dict]:
        """Get available capabilities"""
        return [
            {
                'name': name,
                'commands': list(tool.exec_cmds.keys()),
                'available': tool.available
            }
            for name, tool in self.tools.items()
        ]
    
    def get_execution_log(self, limit: int = 100) -> List[Dict]:
        """Get recent execution history"""
        return self.execution_log[-limit:]


# Export
__all__ = ['CLIIntegrationHub', 'CLICommand']
