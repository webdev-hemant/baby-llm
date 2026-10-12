"""Bi-temporal conflict and contradiction resolver."""

from datetime import datetime, timezone
from typing import List, Optional
from baby_llm.core.models import MemoryCategory, MemoryNode
from baby_llm.retrieval.embedder import get_embedder
from baby_llm.storage.graph_store import BiTemporalGraphStore, graph_store
from baby_llm.storage.vector_store import LanceVectorStore, vector_store


class ConflictResolver:
    def __init__(
        self,
        graph: BiTemporalGraphStore = graph_store,
        vec_store: LanceVectorStore = vector_store,
    ):
        self.graph = graph
        self.vec_store = vec_store

    def resolve_and_commit(
        self,
        subject: str,
        predicate: str,
        object_: str,
        category: MemoryCategory = MemoryCategory.PREFERENCE,
        scope: str = "global",
        confidence: float = 1.0,
        ymyl_protected: bool = False,
        source_turn_id: Optional[str] = None,
    ) -> MemoryNode:
        """
        Applies Bi-temporal resolution with scope isolation:
        1. Checks for existing active node matching (subject, predicate) in scope.
        2. If found and object differs:
           - Marks old node as invalid_from = now.
           - Embeds and inserts new active node.
        3. If matching with same object:
           - Reinforces existing node stability.
        4. If new:
           - Inserts and embeds new node.
        """
        now = datetime.now(timezone.utc)
        active_matches = self.graph.find_active_by_subject_predicate(subject, predicate, scope=scope)

        for old_node in active_matches:
            if old_node.object.lower() == object_.strip().lower():
                # Same fact repeated: reinforce stability
                self.graph.reinforce_node(old_node.id)
                return old_node
            else:
                # Contradiction / Update detected! Close temporal window of old fact
                self.graph.invalidate_node(old_node.id, invalid_time=now)
                self.vec_store.update_active_status(old_node.id, is_active=False)

        # Create and persist new active node
        new_node = MemoryNode(
            subject=subject,
            predicate=predicate,
            object=object_,
            category=category,
            scope=scope.strip().lower() if scope else "global",
            confidence=confidence,
            stability=1.0,
            last_reinforced_at=now,
            valid_from=now,
            invalid_from=None,
            ymyl_protected=ymyl_protected or category in (MemoryCategory.HEALTH, MemoryCategory.FINANCE),
            source_turn_id=source_turn_id,
            created_at=now,
        )

        self.graph.insert_node(new_node)

        # Embed into vector store
        embedder = get_embedder()
        vector = embedder.embed_text(new_node.to_readable_fact())
        self.vec_store.upsert_node(new_node, vector)

        return new_node


conflict_resolver = ConflictResolver()
