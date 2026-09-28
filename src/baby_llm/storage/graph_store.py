"""Bi-temporal Knowledge Graph store backed by SQLite."""

from datetime import datetime
from typing import List, Optional
from baby_llm.core.models import MemoryCategory, MemoryNode
from baby_llm.storage.db import DatabaseManager, db_manager


class BiTemporalGraphStore:
    def __init__(self, db: DatabaseManager = db_manager):
        self.db = db

    def insert_node(self, node: MemoryNode) -> MemoryNode:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO memory_nodes (
                    id, subject, predicate, object, category,
                    confidence, stability, last_reinforced_at,
                    valid_from, invalid_from, ymyl_protected,
                    source_turn_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node.id,
                    node.subject.strip().lower(),
                    node.predicate.strip().lower(),
                    node.object.strip(),
                    node.category.value,
                    node.confidence,
                    node.stability,
                    node.last_reinforced_at.isoformat(),
                    node.valid_from.isoformat(),
                    node.invalid_from.isoformat() if node.invalid_from else None,
                    1 if node.ymyl_protected else 0,
                    node.source_turn_id,
                    node.created_at.isoformat(),
                ),
            )
        return node

    def invalidate_node(self, node_id: str, invalid_time: Optional[datetime] = None) -> None:
        invalid_iso = (invalid_time or datetime.utcnow()).isoformat()
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE memory_nodes SET invalid_from = ? WHERE id = ? AND invalid_from IS NULL",
                (invalid_iso, node_id),
            )

    def reinforce_node(self, node_id: str) -> None:
        """Reinforce memory node upon active recall/reference (doubles stability)."""
        now_iso = datetime.utcnow().isoformat()
        with self.db.get_connection() as conn:
            conn.execute(
                """
                UPDATE memory_nodes
                SET stability = stability * 2.0,
                    last_reinforced_at = ?
                WHERE id = ?
                """,
                (now_iso, node_id),
            )

    def get_node_by_id(self, node_id: str) -> Optional[MemoryNode]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memory_nodes WHERE id = ?",
                (node_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_node(row)

    def get_active_nodes(self, category: Optional[MemoryCategory] = None) -> List[MemoryNode]:
        with self.db.get_connection() as conn:
            if category:
                cursor = conn.execute(
                    "SELECT * FROM memory_nodes WHERE invalid_from IS NULL AND category = ? ORDER BY last_reinforced_at DESC",
                    (category.value,),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM memory_nodes WHERE invalid_from IS NULL ORDER BY last_reinforced_at DESC"
                )
            return [self._row_to_node(r) for r in cursor.fetchall()]

    def find_active_by_subject_predicate(self, subject: str, predicate: str) -> List[MemoryNode]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM memory_nodes
                WHERE subject = ? AND predicate = ? AND invalid_from IS NULL
                """,
                (subject.strip().lower(), predicate.strip().lower()),
            )
            return [self._row_to_node(r) for r in cursor.fetchall()]

    def get_history_for_subject_predicate(self, subject: str, predicate: str) -> List[MemoryNode]:
        """Returns full historical trajectory (both active and expired)."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM memory_nodes
                WHERE subject = ? AND predicate = ?
                ORDER BY valid_from ASC
                """,
                (subject.strip().lower(), predicate.strip().lower()),
            )
            return [self._row_to_node(r) for r in cursor.fetchall()]

    def delete_node(self, node_id: str) -> bool:
        """Glass-box action: Permanently erase a memory node and remove from FTS."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM memory_nodes WHERE id = ?", (node_id,))
            return cursor.rowcount > 0

    def _row_to_node(self, row) -> MemoryNode:
        return MemoryNode(
            id=row["id"],
            subject=row["subject"],
            predicate=row["predicate"],
            object=row["object"],
            category=MemoryCategory(row["category"]),
            confidence=float(row["confidence"]),
            stability=float(row["stability"]),
            last_reinforced_at=datetime.fromisoformat(row["last_reinforced_at"]),
            valid_from=datetime.fromisoformat(row["valid_from"]),
            invalid_from=datetime.fromisoformat(row["invalid_from"]) if row["invalid_from"] else None,
            ymyl_protected=bool(row["ymyl_protected"]),
            source_turn_id=row["source_turn_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


graph_store = BiTemporalGraphStore()
