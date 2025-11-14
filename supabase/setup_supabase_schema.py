#!/usr/bin/env python3
"""
Utility script to apply the Supabase schema definitions that ship with ULTRON.

Reads SQL statements from `supabase/supabase/tables/*.sql` and executes them
against a configured PostgreSQL/Supabase database connection. Connection
details are pulled from environment variables so credentials stay out of the
repository.

Usage:
    export SUPABASE_DB_URL="postgresql://user:pass@host:5432/dbname"
    # (or set POSTGRES_URL / POSTGRES_* variables)
    python supabase/setup_supabase_schema.py
"""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path
from typing import Iterable, Optional

try:
    import psycopg2
    from psycopg2 import errors
except ImportError as exc:  # pragma: no cover - direct feedback is clearer
    sys.stderr.write(
        "psycopg2 is required to run this script. Install with\n"
        "    pip install psycopg2-binary\n"
    )
    raise


ROOT_DIR = Path(__file__).resolve().parent
TABLES_DIR = ROOT_DIR / "supabase" / "tables"


def _collect_sql_files() -> Iterable[Path]:
    if not TABLES_DIR.exists():
        raise FileNotFoundError(f"Supabase tables directory missing: {TABLES_DIR}")
    return sorted(TABLES_DIR.glob("*.sql"))


def _load_connection_url() -> str:
    """
    Resolve the database connection string from environment variables.

    Priority:
      1. SUPABASE_DB_URL
      2. SUPABASE_POSTGRES_URL
      3. POSTGRES_URL
      4. Construct from POSTGRES_HOST/PORT/DB/USER/PASSWORD
    """
    candidates = [
        "SUPABASE_DB_URL",
        "SUPABASE_POSTGRES_URL",
        "POSTGRES_URL",
        "DATABASE_URL",
    ]

    for key in candidates:
        value = os.getenv(key)
        if value:
            return value

    host = os.getenv("POSTGRES_HOST")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DB")
    port = os.getenv("POSTGRES_PORT", "5432")

    if all([host, user, password, database]):
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    required = ", ".join(["SUPABASE_DB_URL", "POSTGRES_URL", "POSTGRES_HOST", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"])
    raise RuntimeError(
        textwrap.dedent(
            f"""
            Database connection details not found.
            Set one of SUPABASE_DB_URL / POSTGRES_URL / DATABASE_URL,
            or configure POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
            POSTGRES_USER, and POSTGRES_PASSWORD.
            Currently checked: {required}
            """
        ).strip()
    )


def _execute_sql_file(cursor, connection, sql_file: Path) -> None:
    raw_sql = sql_file.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in raw_sql.split(";") if stmt.strip()]

    for statement in statements:
        try:
            cursor.execute(statement)
            connection.commit()
            print(f"✓ Applied {sql_file.name}")
        except errors.DuplicateTable:
            connection.rollback()
            print(f"• Skipped {sql_file.name} (table already exists)")
        except Exception as exc:
            connection.rollback()
            print(f"✗ Failed on {sql_file.name}")
            raise RuntimeError(f"Error executing {sql_file.name}: {exc}") from exc


def apply_schema(connection_url: Optional[str] = None) -> None:
    conn_url = connection_url or _load_connection_url()
    sql_files = _collect_sql_files()
    if not sql_files:
        print(f"No SQL files found in {TABLES_DIR}")
        return

    print("Connecting to database...")
    with psycopg2.connect(conn_url) as connection:
        connection.autocommit = False
        with connection.cursor() as cursor:
            cursor.execute("set search_path to public;")

            for sql_file in sql_files:
                _execute_sql_file(cursor, connection, sql_file)


def main() -> None:
    try:
        apply_schema()
        print("Supabase schema applied successfully.")
    except Exception as exc:
        sys.stderr.write(f"Schema setup failed: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
