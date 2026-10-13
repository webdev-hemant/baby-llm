"""Scientific Ebbinghaus Forgetting Curve and YMYL Retention Engine."""

import math
from datetime import datetime, timezone
from typing import List, Tuple
from baby_llm.core.models import MemoryNode, ensure_utc
from baby_llm.storage.graph_store import BiTemporalGraphStore, graph_store
from baby_llm.storage.vector_store import LanceVectorStore, vector_store


class EbbinghausDecayEngine:
    def __init__(
        self,
        graph: BiTemporalGraphStore = graph_store,
        vec_store: LanceVectorStore = vector_store,
        dormant_threshold: float = 0.50,
        archive_threshold: float = 0.20,
    ):
        self.graph = graph
        self.vec_store = vec_store
        self.dormant_threshold = dormant_threshold
        self.archive_threshold = archive_threshold

    def calculate_retention(self, node: MemoryNode, as_of: datetime | None = None) -> float:
        """
        Computes retention probability R(t) = exp(-t / (S * I))
        YMYL (Your Money or Your Life) facts have infinite retention floor (1.0).
        """
        if node.ymyl_protected:
            return 1.0

        current_time = ensure_utc(as_of) or datetime.now(timezone.utc)
        last_reinforced = ensure_utc(node.last_reinforced_at) or current_time
        elapsed_seconds = (current_time - last_reinforced).total_seconds()
        t_days = max(0.0, elapsed_seconds / 86400.0)

        # Importance multiplier: category-based
        importance = self._get_category_importance(node.category.value)
        stability = max(0.1, node.stability)

        exponent = -t_days / (stability * importance)
        retention = math.exp(exponent)
        return float(min(1.0, max(0.0, retention)))

    def evaluate_and_prune(self) -> Tuple[List[str], List[str]]:
        """
        Evaluates all active memory nodes against the decay curve:
        - Active (R >= 0.50)
        - Dormant (0.20 <= R < 0.50)
        - Archived (R < 0.20): Deactivates vector search index
        Returns ([archived_ids], [active_ids]).
        """
        active_nodes = self.graph.get_active_nodes()
        archived_ids = []
        surviving_ids = []

        now = datetime.now(timezone.utc)
        for node in active_nodes:
            r = self.calculate_retention(node, as_of=now)
            if r < self.archive_threshold:
                # Archive node
                self.graph.invalidate_node(node.id, invalid_time=now)
                self.vec_store.update_active_status(node.id, is_active=False)
                archived_ids.append(node.id)
            else:
                surviving_ids.append(node.id)

        return archived_ids, surviving_ids

    def _get_category_importance(self, category: str) -> float:
        weights = {
            "health": 3.0,
            "finance": 3.0,
            "goal": 2.5,
            "work": 2.0,
            "relationship": 2.0,
            "lifestyle": 1.2,
            "preference": 1.0,
        }
        return weights.get(category, 1.0)


decay_engine = EbbinghausDecayEngine()
