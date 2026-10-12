"""Bi-temporal Knowledge Graph store backed by SQLite."""

from datetime import datetime, timezone
from typing import List, Optional
from baby_llm.core.models import MemoryCategory, MemoryNode
from baby_llm.security.encryption import ymyl_encryption
from baby_llm.storage.db import DatabaseManager, db_manager


class BiTemporalGraphStore:
    def __init__(self, db: DatabaseManager = db_manager):
        self.db = db

    def insert_node(self, node: MemoryNode) -> MemoryNode:
        stored_object = node.object.strip()
        if node.ymyl_protected and not ymyl_encryption.is_encrypted(stored_object):
            stored_object = ymyl_encryption.encrypt(stored_object)

        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO memory_nodes (
                    id, subject, predicate, object, category, scope,
                    confidence, stability, last_reinforced_at,
                    valid_from, invalid_from, ymyl_protected,
                    source_turn_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node.id,
                    node.subject.strip().lower(),
                    node.predicate.strip().lower(),
                    stored_object,
                    node.category.value,
                    node.scope.strip().lower() if node.scope else "global",
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
        invalid_iso = (invalid_time or datetime.now(timezone.utc)).isoformat()
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE memory_nodes SET invalid_from = ? WHERE id = ? AND invalid_from IS NULL",
                (invalid_iso, node_id),
            )

    def reinforce_node(self, node_id: str) -> None:
        """Reinforce memory node upon active recall/reference (doubles stability)."""
        now_iso = datetime.now(timezone.utc).isoformat()
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

    def get_active_nodes(
        self,
        category: Optional[MemoryCategory] = None,
        scope: Optional[str] = None,
    ) -> List[MemoryNode]:
        with self.db.get_connection() as conn:
            query = "SELECT * FROM memory_nodes WHERE invalid_from IS NULL"
            params = []

            if category:
                query += " AND category = ?"
                params.append(category.value)

            if scope and scope.lower() != "all":
                query += " AND (scope = ? OR scope = 'global')"
                params.append(scope.strip().lower())

            query += " ORDER BY last_reinforced_at DESC"
            cursor = conn.execute(query, tuple(params))
            return [self._row_to_node(r) for r in cursor.fetchall()]

    def find_active_by_subject_predicate(
        self,
        subject: str,
        predicate: str,
        scope: Optional[str] = None,
    ) -> List[MemoryNode]:
        with self.db.get_connection() as conn:
            query = """
                SELECT * FROM memory_nodes
                WHERE subject = ? AND predicate = ? AND invalid_from IS NULL
            """
            params = [subject.strip().lower(), predicate.strip().lower()]

            if scope and scope.lower() != "all":
                query += " AND (scope = ? OR scope = 'global')"
                params.append(scope.strip().lower())

            cursor = conn.execute(query, tuple(params))
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

    def get_entity_subgraph(
        self,
        entity: str,
        max_hops: int = 1,
        scope: Optional[str] = None,
    ) -> List[MemoryNode]:
        """
        Traverse 1-hop or 2-hop active memory connections centered on an entity.
        Matches where entity is subject or contained in object.
        """
        clean_ent = entity.strip().lower()
        active_nodes = self.get_active_nodes(scope=scope)
        
        # 1-Hop matching
        first_hop = []
        neighbor_entities = set()
        for node in active_nodes:
            s_match = (node.subject.lower() == clean_ent or clean_ent in node.subject.lower())
            o_match = (clean_ent in node.object.lower())
            if s_match or o_match:
                first_hop.append(node)
                neighbor_entities.add(node.subject.lower())
                # Add token words from object if not too short
                for tok in node.object.lower().split():
                    if len(tok) > 3 and tok.isalnum():
                        neighbor_entities.add(tok)

        if max_hops <= 1 or not neighbor_entities:
            return first_hop

        # 2-Hop expansion
        visited_ids = {n.id for n in first_hop}
        second_hop = list(first_hop)
        for node in active_nodes:
            if node.id in visited_ids:
                continue
            if node.subject.lower() in neighbor_entities or any(n in node.object.lower() for n in neighbor_entities):
                second_hop.append(node)
                visited_ids.add(node.id)

        return second_hop

    def delete_node(self, node_id: str) -> bool:
        """Glass-box action: Permanently erase a memory node and remove from FTS."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM memory_nodes WHERE id = ?", (node_id,))
            return cursor.rowcount > 0

    def _row_to_node(self, row) -> MemoryNode:
        is_ymyl = bool(row["ymyl_protected"])
        raw_object = row["object"]
        if is_ymyl and ymyl_encryption.is_encrypted(raw_object):
            plain_object = ymyl_encryption.decrypt(raw_object)
        else:
            plain_object = raw_object

        scope_val = "global"
        try:
            if "scope" in row.keys() and row["scope"]:
                scope_val = row["scope"]
        except Exception:
            pass

        return MemoryNode(
            id=row["id"],
            subject=row["subject"],
            predicate=row["predicate"],
            object=plain_object,
            category=MemoryCategory(row["category"]),
            scope=scope_val,
            confidence=float(row["confidence"]),
            stability=float(row["stability"]),
            last_reinforced_at=datetime.fromisoformat(row["last_reinforced_at"]),
            valid_from=datetime.fromisoformat(row["valid_from"]),
            invalid_from=datetime.fromisoformat(row["invalid_from"]) if row["invalid_from"] else None,
            ymyl_protected=is_ymyl,
            source_turn_id=row["source_turn_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


graph_store = BiTemporalGraphStore()
