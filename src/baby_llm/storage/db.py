"""SQLite connection manager and schema migrations for Baby LLM."""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
from baby_llm.config import settings


SCHEMA_SQL = """
-- 1. Write-Ahead Interaction Log
CREATE TABLE IF NOT EXISTS interaction_log (
    turn_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_input TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    sentiment_tag TEXT,
    processed_in_dream BOOLEAN DEFAULT 0
);

-- 2. Core Bi-Temporal Memory Nodes
CREATE TABLE IF NOT EXISTS memory_nodes (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    category TEXT CHECK(category IN ('lifestyle', 'health', 'finance', 'work', 'relationship', 'goal', 'preference')),
    scope TEXT DEFAULT 'global',
    confidence REAL DEFAULT 1.0,
    stability REAL DEFAULT 1.0,
    last_reinforced_at TIMESTAMP NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    invalid_from TIMESTAMP,
    ymyl_protected BOOLEAN DEFAULT 0,
    source_turn_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_memory_active ON memory_nodes (invalid_from) WHERE invalid_from IS NULL;
CREATE INDEX IF NOT EXISTS idx_memory_category ON memory_nodes (category);
CREATE INDEX IF NOT EXISTS idx_memory_subject ON memory_nodes (subject);

-- 3. Full-Text Search Virtual Table (FTS5)
CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    node_id UNINDEXED,
    subject,
    predicate,
    object,
    category,
    tokenize = 'porter unicode61'
);

-- Triggers for keeping FTS5 in sync with memory_nodes
CREATE TRIGGER IF NOT EXISTS trg_memory_nodes_ai AFTER INSERT ON memory_nodes BEGIN
    INSERT INTO memory_fts(node_id, subject, predicate, object, category)
    VALUES (new.id, new.subject, new.predicate, new.object, new.category);
END;

CREATE TRIGGER IF NOT EXISTS trg_memory_nodes_ad AFTER DELETE ON memory_nodes BEGIN
    DELETE FROM memory_fts WHERE node_id = old.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_memory_nodes_au AFTER UPDATE ON memory_nodes BEGIN
    DELETE FROM memory_fts WHERE node_id = old.id;
    INSERT INTO memory_fts(node_id, subject, predicate, object, category)
    VALUES (new.id, new.subject, new.predicate, new.object, new.category);
END;

-- 4. Commitments & Success Tracking
CREATE TABLE IF NOT EXISTS commitments (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'dropped')) DEFAULT 'pending',
    target_deadline TIMESTAMP,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    associated_node_id TEXT REFERENCES memory_nodes(id)
);

-- 5. Daily Morning / Evening Briefings
CREATE TABLE IF NOT EXISTS daily_summaries (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL UNIQUE,
    summary_type TEXT CHECK(summary_type IN ('morning_brief', 'evening_reflection')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class DatabaseManager:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or settings.db_path
        self._ensure_db()

    def _ensure_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.get_connection() as conn:
            # Idempotent migration: ensure scope column exists on pre-existing tables
            try:
                cursor = conn.execute("PRAGMA table_info(memory_nodes)")
                cols = [row["name"] for row in cursor.fetchall()]
                if cols and "scope" not in cols:
                    conn.execute("ALTER TABLE memory_nodes ADD COLUMN scope TEXT DEFAULT 'global'")
            except Exception:
                pass

            conn.executescript(SCHEMA_SQL)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_scope ON memory_nodes (scope)")

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


db_manager = DatabaseManager()
