#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Windows Compatible Main Entry Point
Enhanced with Elite Brain, Semantic Memory, and RAG capabilities
"""

import asyncio
import sys
import signal
import logging
import os
import json
import hashlib
import time
import sqlite3
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque, defaultdict
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ── Configuration ──────────────────────────────────────────────────────────────
MEMORY_FILE = Path("ultron_memory.json")
RAG_DB_PATH = Path(".ultron/rag.db")
MAX_CONTEXT_TOKENS = 8000
CHUNK_SIZE = 1400
CHUNK_OVERLAP = 220
TOOL_CACHE_TTL = 300  # seconds

# ── Data Classes ───────────────────────────────────────────────────────────────


@dataclass
class Message:
    """Single conversation message with metadata."""
    role: str
    content: str
    timestamp: float = field(
        default_factory=lambda: datetime.now().timestamp())
    tokens: int = 0
    relevance_score: float = 1.0
    is_summary: bool = False


@dataclass
class ToolResult:
    """Standard tool execution result."""
    tool: str
    args: dict[str, Any]
    result: str
    duration_ms: float
    success: bool
    error: str | None = None
    timestamp: float = field(
        default_factory=lambda: datetime.now().timestamp())
    cache_hit: bool = False


@dataclass
class MemoryEntry:
    """Semantic memory entry."""
    uid: str
    text: str
    source: str  # "fact" | "episodic" | "tool" | "observation"
    timestamp: float
    access_count: int = 0
    importance: float = 1.0

# ── Context Optimizer (from Vision elite_memory.py) ──────────────────────


class ContextOptimizer:
    """Sliding window context management with token budgeting."""

    def __init__(self, max_tokens: int = MAX_CONTEXT_TOKENS):
        self.max_tokens = max_tokens
        self.messages: list[Message] = []
        self.total_tokens = 0

    def add_message(self, role: str, content: str, tokens: int = 0) -> None:
        """Add message and trim if over limit."""
        msg = Message(
            role=role,
            content=content,
            tokens=tokens or len(content) // 4,
        )
        self.messages.append(msg)
        self.total_tokens += msg.tokens
        self._trim_context()

    def _trim_context(self) -> None:
        """Remove least relevant messages to fit token budget."""
        while self.total_tokens > self.max_tokens and len(self.messages) > 1:
            candidates = [
                (i, m) for i, m in enumerate(self.messages)
                if m.role != "system"
            ]
            if not candidates:
                break
            idx, msg = min(candidates, key=lambda x: x[1].timestamp)
            self.messages.pop(idx)
            self.total_tokens -= msg.tokens

    def get_context(self) -> list[dict[str, str]]:
        """Return optimized context for LLM."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def search(self, query: str, top_k: int = 3) -> list[str]:
        """Simple keyword search in context."""
        query_words = set(query.lower().split())
        scores: dict[int, float] = {}

        for i, msg in enumerate(self.messages):
            msg_words = set(msg.content.lower().split())
            overlap = len(query_words & msg_words)
            if overlap > 0:
                scores[i] = overlap

        top_indices = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
        return [self.messages[i].content for i, _ in top_indices]

# ── Tool Cache & Executor (from Vision elite_tools.py) ───────────────────


class ToolCache:
    """Cache tool results with TTL."""

    def __init__(self, ttl_seconds: int = TOOL_CACHE_TTL):
        self.cache: dict[str, tuple[str, float]] = {}
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0

    def _key(self, tool: str, args: Mapping[str, Any]) -> str:
        content = f"{tool}:{json.dumps(args, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, tool: str, args: Mapping[str, Any]) -> str | None:
        key = self._key(tool, args)
        if key in self.cache:
            result, expiry = self.cache[key]
            if time.time() < expiry:
                self.hits += 1
                return result
            del self.cache[key]
        self.misses += 1
        return None

    def set(self, tool: str, args: Mapping[str, Any], result: str) -> None:
        key = self._key(tool, args)
        expiry = time.time() + self.ttl_seconds
        self.cache[key] = (result, expiry)

    def stats(self) -> dict[str, Any]:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total, 3) if total > 0 else 0.0,
            "size": len(self.cache),
        }


class SafeToolExecutor:
    """Execute tools with safety checks, caching, and analytics."""

    def __init__(self):
        self.cache = ToolCache()
        self.analytics: dict[str, list[float]] = defaultdict(list)
        self.max_parallel = 5
        self.semaphore = asyncio.Semaphore(self.max_parallel)
        self.blocked_tools: set = set()

    async def execute(
        self,
        tool: str,
        args: Mapping[str, Any],
        executor_fn: Callable[[str, Mapping[str, Any]], Awaitable[str]],
        cacheable: bool = True,
        timeout_seconds: float = 30.0,
    ) -> ToolResult:
        """Execute tool with safety and caching."""
        if tool in self.blocked_tools:
            return ToolResult(
                tool=tool, args=dict(args), result="",
                duration_ms=0, success=False,
                error=f"Tool {tool} is blocked"
            )

        if cacheable:
            cached = self.cache.get(tool, args)
            if cached:
                return ToolResult(
                    tool=tool, args=dict(args), result=cached,
                    duration_ms=0, success=True, cache_hit=True
                )

        async with self.semaphore:
            start = time.monotonic()
            try:
                result = await asyncio.wait_for(
                    executor_fn(tool, args), timeout=timeout_seconds
                )
                duration_ms = (time.monotonic() - start) * 1000
                if cacheable:
                    self.cache.set(tool, args, result)
                self.analytics[tool].append(duration_ms)
                return ToolResult(
                    tool=tool, args=dict(args), result=result,
                    duration_ms=duration_ms, success=True
                )
            except asyncio.TimeoutError:
                return ToolResult(
                    tool=tool, args=dict(args), result="",
                    duration_ms=(time.monotonic() - start) * 1000,
                    success=False, error=f"Timeout after {timeout_seconds}s"
                )
            except Exception as e:
                return ToolResult(
                    tool=tool, args=dict(args), result="",
                    duration_ms=(time.monotonic() - start) * 1000,
                    success=False, error=str(e)[:200]
                )

    def analytics_summary(self) -> dict[str, Any]:
        return {
            "cache": self.cache.stats(),
            "tools": {
                tool: {
                    "executions": len(d),
                    "avg_duration_ms": round(sum(d) / len(d), 2),
                    "min_ms": round(min(d), 2),
                    "max_ms": round(max(d), 2),
                }
                for tool, d in self.analytics.items() if d
            },
            "blocked": list(self.blocked_tools),
        }

# ── RAG Manager (from Vision vision_rag.py) ──────────────────────────────


class UltronRAGManager:
    """RAG manager with SQLite FTS5 backend for local knowledge."""

    SUPPORTED_EXTENSIONS = {
        ".txt", ".md", ".markdown", ".rst", ".json", ".jsonl",
        ".csv", ".tsv", ".yaml", ".yml", ".py", ".js", ".ts",
        ".html", ".htm", ".xml", ".sql", ".sh", ".ps1", ".bat",
        ".toml", ".ini", ".cfg",
    }

    SKIP_DIRS = {
        ".git", ".venv", "venv", "node_modules", "__pycache__",
        ".pytest_cache", ".mypy_cache", ".ruff_cache",
    }

    def __init__(self, db_path: Path = RAG_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    rel_path TEXT NOT NULL,
                    abs_path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    char_count INTEGER NOT NULL,
                    token_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
                USING fts5(chunk_id UNINDEXED, rel_path, content, tokenize='unicode61');
                CREATE INDEX IF NOT EXISTS idx_chunks_rel_path ON chunks(rel_path);
            """)

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        cleaned = "\n".join(line.rstrip() for line in text.splitlines()).strip()
        if not cleaned:
            return []

        paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
        chunks: list[str] = []
        current = ""

        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
            if len(candidate) <= CHUNK_SIZE:
                current = candidate
                continue

            if current:
                chunks.append(current)

            if len(paragraph) <= CHUNK_SIZE:
                current = paragraph
                continue

            start = 0
            while start < len(paragraph):
                end = min(len(paragraph), start + CHUNK_SIZE)
                piece = paragraph[start:end].strip()
                if piece:
                    chunks.append(piece)
                if end >= len(paragraph):
                    break
                start = max(0, end - CHUNK_OVERLAP)
            current = ""

        if current:
            chunks.append(current)

        return chunks

    def index_file(self, file_path: Path) -> int:
        """Index a single file into RAG."""
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return 0

        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            chunks = self._chunk_text(text)

            with self._connect() as conn:
                count = 0
                for i, chunk in enumerate(chunks):
                    chunk_id = hashlib.md5(
                        f"{file_path}:{i}".encode()
                    ).hexdigest()
                    conn.execute("""
                        INSERT OR REPLACE INTO chunks
                        (chunk_id, rel_path, abs_path, content,
                         char_count, token_count, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        chunk_id, str(file_path),
                        str(file_path.absolute()),
                        chunk, len(chunk), len(chunk) // 4,
                        datetime.now().isoformat()
                    ))
                    conn.execute("""
                        INSERT OR REPLACE INTO chunks_fts
                        (chunk_id, rel_path, content)
                        VALUES (?, ?, ?)
                    """, (chunk_id, str(file_path), chunk))
                    count += 1
                return count
        except Exception as e:
            logging.warning(f"Failed to index {file_path}: {e}")
            return 0

    def index_directory(
        self, directory: Path, max_files: int = 0
    ) -> dict[str, Any]:
        """Index all supported files in directory."""
        files = []
        for candidate in directory.rglob("*"):
            if max_files and len(files) >= max_files:
                break
            if not candidate.is_file():
                continue
            if any(part in self.SKIP_DIRS for part in candidate.parts):
                continue
            if candidate.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    if candidate.stat().st_size <= 6 * 1024 * 1024:  # 6MB limit
                        files.append(candidate)
                except OSError:
                    continue

        total_chunks = 0
        for file_path in files:
            total_chunks += self.index_file(file_path)

        return {
            "files_indexed": len(files),
            "chunks_created": total_chunks,
            "directory": str(directory),
        }

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Search RAG for relevant chunks."""
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT c.chunk_id, c.rel_path, c.content,
                       rank AS score
                FROM chunks_fts fts
                JOIN chunks c ON c.chunk_id = fts.chunk_id
                WHERE chunks_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, top_k))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "chunk_id": row[0],
                    "path": row[1],
                    "content": row[2],
                    "score": row[3],
                })
            return results

# ── Enhanced ULTRON Agent ─────────────────────────────────────────────────


class EnhancedUltronAgent:
    """Enhanced ULTRON Agent with Elite Brain capabilities."""

    def __init__(self):
        self.status = "initializing"
        self.tools: dict[str, Any] = {}
        self.context_opt = ContextOptimizer()
        self.tool_executor = SafeToolExecutor()
        self.rag = UltronRAGManager()
        self.memory: dict[str, Any] = {
            "facts": {}, "episodes": deque(maxlen=500)
        }
        self.start_time = time.time()
        self.command_count = 0

        # Load environment config
        self.config = self._load_env_config()

        print(f"[INFO] Enhanced ULTRON Agent initialized")
        print(f"[INFO] Platform: {os.name} (nt=Windows)")
        print(f"[INFO] PID: {os.getpid()}")
        print(f"[INFO] CWD: {os.getcwd()}")

    def _load_env_config(self) -> dict[str, str]:
        """Load configuration from environment variables."""
        return {
            "llm_model": os.environ.get("ULTRON_LLM_MODEL", "llama3.2"),
            "ollama_url": os.environ.get(
                "ULTRON_OLLAMA_URL", "http://localhost:11434"
            ),
            "voice_enabled": (
                os.environ.get("ULTRON_VOICE", "false").lower() == "true"
            ),
            "rag_enabled": (
                os.environ.get("ULTRON_RAG", "true").lower() == "true"
            ),
            "memory_file": os.environ.get(
                "ULTRON_MEMORY_FILE", "ultron_memory.json"
            ),
        }

    async def initialize(self):
        """Initialize all subsystems."""
        try:
            # Create necessary directories
            os.makedirs("logs", exist_ok=True)
            os.makedirs("data", exist_ok=True)
            os.makedirs(".ultron", exist_ok=True)

            # Load persistent memory
            self._load_memory()

            # Index current directory for RAG
            if self.config.get("rag_enabled"):
                print("[INFO] Indexing project for RAG...")
                result = self.rag.index_directory(Path("."), max_files=100)
                print(
                    f"[INFO] RAG indexed: {result['files_indexed']} files,"
                    f" {result['chunks_created']} chunks"
                )

            self.status = "ready"
            print("[INFO] ULTRON Agent ready with Elite Brain capabilities")
            return True
        except Exception as e:
            print(f"[ERROR] Initialization failed: {e}")
            self.status = "error"
            return False

    def _load_memory(self) -> None:
        """Load persistent memory from disk."""
        memory_path = Path(self.config.get("memory_file", "ultron_memory.json"))
        if memory_path.exists():
            try:
                data = json.loads(memory_path.read_text(encoding="utf-8"))
                self.memory["facts"] = data.get("facts", {})
                facts = len(self.memory['facts'])
                print(f"[INFO] Loaded {facts} fact categories from memory")
            except Exception as e:
                print(f"[WARNING] Failed to load memory: {e}")

    def _save_memory(self) -> None:
        """Save memory to disk."""
        memory_path = Path(self.config.get("memory_file", "ultron_memory.json"))
        try:
            data = {
                "facts": self.memory["facts"],
                "updated": datetime.now().isoformat(),
            }
            memory_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[WARNING] Failed to save memory: {e}")

    def add_fact(self, category: str, fact: str) -> None:
        """Add a fact to semantic memory."""
        if category not in self.memory["facts"]:
            self.memory["facts"][category] = []
        self.memory["facts"][category].append(fact)
        self._save_memory()

    def get_facts(self, category: str) -> list[str]:
        """Retrieve facts by category."""
        return self.memory["facts"].get(category, [])

    def search_memory(self, query: str) -> list[str]:
        """Search both context and RAG for relevant information."""
        results = []

        # Search context
        context_results = self.context_opt.search(query, top_k=3)
        results.extend(context_results)

        # Search RAG
        rag_results = self.rag.search(query, top_k=3)
        for r in rag_results:
            results.append(f"[RAG:{r['path']}] {r['content'][:200]}...")

        return results

    async def execute_tool(
        self, tool_name: str, args: dict[str, Any]
    ) -> ToolResult:
        """Execute a tool with caching and safety."""
        async def executor(tool: str, tool_args: Mapping[str, Any]) -> str:
            # Tool execution logic here
            if tool == "system_info":
                return json.dumps({
                    "platform": os.name,
                    "pid": os.getpid(),
                    "cwd": os.getcwd(),
                    "env": dict(os.environ) if tool_args.get("full_env") else {},
                })
            elif tool == "file_read":
                path = Path(tool_args.get("path", ""))
                if path.exists():
                    return path.read_text(
                        encoding="utf-8", errors="ignore")[:1000]
                return "File not found"
            elif tool == "file_write":
                path = Path(tool_args.get("path", ""))
                content = tool_args.get("content", "")
                path.write_text(content, encoding="utf-8")
                return f"Written {len(content)} chars to {path}"
            elif tool == "rag_search":
                results = self.rag.search(tool_args.get("query", ""), top_k=5)
                return json.dumps(results)
            elif tool == "list_dir":
                path = Path(tool_args.get("path", "."))
                items = [f"{'[DIR]' if p.is_dir() else '[FILE]'} {p.name}"
                        for p in path.iterdir()]
                return "\n".join(items)
            else:
                return f"Unknown tool: {tool}"

        return await self.tool_executor.execute(tool_name, args, executor)

    def process_command(self, command: str) -> str:
        """Process command with context awareness."""
        self.command_count += 1

        # Add to context
        self.context_opt.add_message("user", command)

        # Parse special commands
        cmd_lower = command.lower().strip()

        if cmd_lower == "status":
            uptime = time.time() - self.start_time
            cache_stats = self.tool_executor.cache.stats()
            return f"""Status: {self.status}
Uptime: {uptime:.1f}s
Commands processed: {self.command_count}
Cache hit rate: {cache_stats['hit_rate']:.1%}
Memory facts: {sum(len(v) for v in self.memory['facts'].values())}
Context messages: {len(self.context_opt.messages)}"""

        elif cmd_lower.startswith("remember "):
            fact = command[9:].strip()
            self.add_fact("general", fact)
            return f"Remembered: {fact}"

        elif cmd_lower.startswith("recall "):
            query = command[7:].strip()
            results = self.search_memory(query)
            if results:
                return "Relevant information:\n" + "\n---\n".join(results[:5])
            return "No relevant information found."

        elif cmd_lower.startswith("rag "):
            query = command[4:].strip()
            results = self.rag.search(query, top_k=5)
            if results:
                output = []
                for r in results:
                    output.append(f"📄 {r['path']}\n{r['content'][:300]}...")
                return "\n\n".join(output)
            return "No RAG results found."

        elif cmd_lower.startswith("tool "):
            parts = command[5:].strip().split(" ", 1)
            tool_name = parts[0]
            tool_args = json.loads(parts[1]) if len(parts) > 1 else {}

            import asyncio
            result = asyncio.run(self.execute_tool(tool_name, tool_args))
            status = "✅" if result.success else "❌"
            return f"{status} {result.tool}: {result.result[:500]}"

        elif cmd_lower == "analytics":
            return json.dumps(self.tool_executor.analytics_summary(), indent=2)

        elif cmd_lower == "env":
            env_vars = {
                k: v for k, v in os.environ.items()
                if not any(
                    s in k.lower()
                    for s in ["key", "token", "secret", "password"]
                )
            }
            return json.dumps(env_vars, indent=2)

        elif cmd_lower == "help":
            return """Available commands:
  status - Show agent status and metrics
  remember <fact> - Store a fact in memory
  recall <query> - Search memory and RAG
  rag <query> - Search RAG index
  tool <name> [args] - Execute a tool
  analytics - Show tool execution analytics
  env - Show environment variables
  help - Show this help
  exit - Exit the agent"""

        else:
            # Default: search for context and provide intelligent response
            context = self.search_memory(command)
            response = f"Command received: {command}"
            if context:
                response += f"\n\nContext found:\n" + "\n".join(context[:3])

            self.context_opt.add_message("assistant", response)
            return response


def setup_signal_handlers():
    """Setup graceful shutdown on signals."""
    def signal_handler(signum, frame):
        print(
            f"\nReceived signal {signum}, shutting down gracefully..."
        )
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main entry point with enhanced capabilities."""
    try:
        # Setup enhanced logging
        os.makedirs("logs", exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("logs/ultron.log", encoding="utf-8"),
            ]
        )
        logger = logging.getLogger(__name__)

        logger.info("=" * 60)
        logger.info("ULTRON Agent 3.0 - Enhanced Windows Edition")
        logger.info("=" * 60)
        logger.info("Features: Elite Brain | Semantic Memory | RAG | Tool Cache")
        logger.info("=" * 60)

        # Setup signal handlers
        setup_signal_handlers()

        # Initialize enhanced agent
        agent = EnhancedUltronAgent()

        # Initialize the agent
        asyncio.run(agent.initialize())

        facts_count = sum(len(v) for v in agent.memory['facts'].values())
        print("\n - main_windows.py:709" + "="*60)
        print("ULTRON Agent 3.0  Enhanced Windows Mode - main_windows.py:710")
        print("= - main_windows.py:711"*60)
        print(f"Status: {agent.status.upper()} - main_windows.py:712")
        print(f"Memory: {facts_count} facts - main_windows.py:713")
        print(f"Cache: Ready (TTL: {TOOL_CACHE_TTL}s) - main_windows.py:714")
        print("RAG: Indexed and ready - main_windows.py:715")
        print("Commands: - main_windows.py:716")
        print("help       Show all commands - main_windows.py:717")
        print("status     System status and metrics - main_windows.py:718")
        print("remember   Store a fact in memory - main_windows.py:719")
        print("recall     Search memory and RAG - main_windows.py:720")
        print("rag        Search RAG index - main_windows.py:721")
        print("tool       Execute a tool - main_windows.py:722")
        print("analytics  Tool performance stats - main_windows.py:723")
        print("exit       Shutdown gracefully - main_windows.py:724")
        print("= - main_windows.py:725"*60)

        # Enhanced CLI loop
        while True:
            try:
                command = input("\n🤖 ULTRON> ").strip()
                if command.lower() in ['exit', 'quit', 'q']:
                    print("\nSaving memory... - main_windows.py:732")
                    agent._save_memory()
                    print("Shutting down ULTRON Agent... - main_windows.py:734")
                    break
                elif command.lower() == 'help':
                    print(agent.process_command("help - main_windows.py:737"))
                elif command.lower() == 'status':
                    print(agent.process_command("status - main_windows.py:739"))
                elif command.lower().startswith('remember '):
                    print(agent.process_command(command))
                elif command.lower().startswith('recall '):
                    print(agent.process_command(command))
                elif command.lower().startswith('rag '):
                    print(agent.process_command(command))
                elif command.lower().startswith('tool '):
                    print(agent.process_command(command))
                elif command.lower() == 'analytics':
                    print(agent.process_command("analytics - main_windows.py:749"))
                elif command.lower() == 'env':
                    print(agent.process_command("env - main_windows.py:751"))
                elif command:
                    response = agent.process_command(command)
                    print(f"Response: {response} - main_windows.py:754")

            except KeyboardInterrupt:
                print("\nSaving memory... - main_windows.py:757")
                agent._save_memory()
                print("Shutting down ULTRON Agent... - main_windows.py:759")
                break
            except EOFError:
                print("\nSaving memory... - main_windows.py:762")
                agent._save_memory()
                print("Shutting down ULTRON Agent... - main_windows.py:764")
                break

        return 0

    except Exception as e:
        error_msg = f"ULTRON Agent startup failed: {str(e)}"
        print(error_msg, file=sys.stderr)
        logging.error(error_msg, exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
