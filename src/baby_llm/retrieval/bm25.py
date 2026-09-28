"""Full-Text BM25 search over memory nodes using SQLite FTS5."""

from typing import List, Tuple
from baby_llm.storage.db import DatabaseManager, db_manager


class BM25Retriever:
    def __init__(self, db: DatabaseManager = db_manager):
        self.db = db

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Executes BM25 search across subject, predicate, and object.
        Returns list of (node_id, bm25_rank_score).
        """
        sanitized_query = "".join(c if c.isalnum() or c.isspace() else " " for c in query).strip()
        if not sanitized_query:
            return []

        tokens = sanitized_query.split()
        match_phrase = " OR ".join(f'"{token}"' for token in tokens if len(token) > 1)
        if not match_phrase:
            return []

        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT m.node_id, bm25(memory_fts) as score
                FROM memory_fts m
                JOIN memory_nodes n ON m.node_id = n.id
                WHERE memory_fts MATCH ? AND n.invalid_from IS NULL
                ORDER BY score ASC
                LIMIT ?
                """,
                (match_phrase, top_k),
            )
            rows = cursor.fetchall()
            # SQLite bm25() returns lower (more negative) values for better matches
            return [(row["node_id"], float(row["score"])) for row in rows]


bm25_retriever = BM25Retriever()
