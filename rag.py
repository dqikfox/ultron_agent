"""
ULTRON Agent - Repo RAG
Indexes key source files and docs into SQLite FTS5.
Usage:
    python rag.py index          # index the repo
    python rag.py query "..."    # search indexed content
    python rag.py stats          # show index stats
"""

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
DB_PATH = ROOT / ".ultron" / "rag.db"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

SOURCE_EXTENSIONS = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml",
    ".toml", ".cfg", ".ini", ".bat", ".sh", ".ts", ".js",
}

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "repomix_output", "screenshots", "images", "models",
    "cache", ".ultron",
}

# Only index files under these subdirs (keeps index focused)
INCLUDE_ROOTS = {
    "tools", "utils", "docs", "tests", "gui",
    "voice", "memory", "scripts",
}

# Plus these specific root-level files
INCLUDE_ROOT_FILES = {
    "main.py", "main_windows.py", "agent_core.py", "brain.py",
    "voice.py", "voice_manager.py", "vision.py", "config.py",
    "memory.py", "console_ai_agent.py", "README.md",
    "requirements.txt", "ultron_config.json", "pyproject.toml",
}


# ── DB ────────────────────────────────────────────────────────────────────────

def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def ensure_schema() -> None:
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id   TEXT PRIMARY KEY,
                rel_path   TEXT NOT NULL,
                content    TEXT NOT NULL,
                char_count INTEGER NOT NULL
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
            USING fts5(
                chunk_id UNINDEXED,
                rel_path,
                content,
                tokenize='unicode61'
            );
            CREATE INDEX IF NOT EXISTS idx_rel_path
            ON chunks(rel_path);
        """)


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_text(text: str) -> list[str]:
    cleaned = "\n".join(l.rstrip() for l in text.splitlines()).strip()
    if not cleaned:
        return []

    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= CHUNK_SIZE:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(para) <= CHUNK_SIZE:
            current = para
            continue
        start = 0
        while start < len(para):
            end = min(len(para), start + CHUNK_SIZE)
            piece = para[start:end].strip()
            if piece:
                chunks.append(piece)
            if end >= len(para):
                break
            start = max(0, end - CHUNK_OVERLAP)
        current = ""

    if current:
        chunks.append(current)
    return chunks


# ── Indexing ──────────────────────────────────────────────────────────────────

def should_index(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return False
    if path.suffix.lower() not in SOURCE_EXTENSIONS:
        return False
    # Always include specific root files
    if path.parent == ROOT and path.name in INCLUDE_ROOT_FILES:
        return True
    # Include files under focused subdirs
    for part in path.relative_to(ROOT).parts[:-1]:
        if part in INCLUDE_ROOTS:
            return True
    return False


def index_file(path: Path, conn: sqlite3.Connection) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0

    rel = str(path.relative_to(ROOT))
    chunks = chunk_text(text)
    count = 0

    for i, chunk in enumerate(chunks):
        cid = hashlib.md5(f"{rel}:{i}".encode()).hexdigest()
        conn.execute(
            "INSERT OR REPLACE INTO chunks "
            "(chunk_id, rel_path, content, char_count) "
            "VALUES (?, ?, ?, ?)",
            (cid, rel, chunk, len(chunk)),
        )
        conn.execute(
            "INSERT OR REPLACE INTO chunks_fts "
            "(chunk_id, rel_path, content) VALUES (?, ?, ?)",
            (cid, rel, chunk),
        )
        count += 1
    return count


def index_repo() -> dict[str, int]:
    ensure_schema()
    files_done = 0
    chunks_done = 0

    with get_conn() as conn:
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            if path.stat().st_size > 4 * 1024 * 1024:
                continue
            if not should_index(path):
                continue
            n = index_file(path, conn)
            if n:
                files_done += 1
                chunks_done += n

    return {"files": files_done, "chunks": chunks_done}


# ── Search ────────────────────────────────────────────────────────────────────

def search(
    query: str, top_k: int = 8
) -> list[dict[str, str | float]]:
    ensure_schema()
    with get_conn() as conn:
        cursor = conn.execute(
            """
            SELECT c.rel_path, c.content, rank AS score
            FROM chunks_fts fts
            JOIN chunks c ON c.chunk_id = fts.chunk_id
            WHERE chunks_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (query, top_k),
        )
        return [
            {"path": r[0], "content": r[1], "score": r[2]}
            for r in cursor.fetchall()
        ]


def stats() -> dict[str, int]:
    ensure_schema()
    with get_conn() as conn:
        files = conn.execute(
            "SELECT COUNT(DISTINCT rel_path) FROM chunks"
        ).fetchone()[0]
        chunks = conn.execute(
            "SELECT COUNT(*) FROM chunks"
        ).fetchone()[0]
    return {"indexed_files": files, "total_chunks": chunks}


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] == "index":
        print("Indexing repo...")
        result = index_repo()
        print(
            f"Done: {result['files']} files, "
            f"{result['chunks']} chunks indexed."
        )

    elif args[0] == "query":
        if len(args) < 2:
            print("Usage: python rag.py query \"your question\"")
            sys.exit(1)
        query = " ".join(args[1:])
        results = search(query)
        if not results:
            print("No results found.")
            return
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r['path']}")
            print("-" * 60)
            print(str(r["content"])[:400])

    elif args[0] == "stats":
        s = stats()
        print(json.dumps(s, indent=2))

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
