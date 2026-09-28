"""Hybrid Retriever fusing BM25 and Vector Search with Reciprocal Rank Fusion (RRF)."""

from typing import Dict, List, Optional
from baby_llm.config import settings
from baby_llm.core.models import RetrievedMemory
from baby_llm.retrieval.bm25 import BM25Retriever, bm25_retriever
from baby_llm.retrieval.embedder import LocalEmbedder, get_embedder
from baby_llm.storage.graph_store import BiTemporalGraphStore, graph_store
from baby_llm.storage.vector_store import LanceVectorStore, vector_store


class HybridRetriever:
    def __init__(
        self,
        embedder: Optional[LocalEmbedder] = None,
        vec_store: LanceVectorStore = vector_store,
        bm25: BM25Retriever = bm25_retriever,
        graph: BiTemporalGraphStore = graph_store,
        rrf_k: int = settings.rrf_k_constant,
    ):
        self._embedder = embedder
        self.vec_store = vec_store
        self.bm25 = bm25
        self.graph = graph
        self.rrf_k = rrf_k

    @property
    def embedder(self) -> LocalEmbedder:
        if self._embedder is None:
            self._embedder = get_embedder()
        return self._embedder

    def retrieve(self, query: str, top_k: int = settings.hybrid_top_k) -> List[RetrievedMemory]:
        """
        Executes sub-20ms hybrid retrieval:
        1. BM25 rank over SQLite FTS5.
        2. Cosine distance rank over LanceDB.
        3. Reciprocal Rank Fusion calculation.
        """
        # 1. BM25 Search
        bm25_matches = self.bm25.search(query, top_k=top_k * 2)

        # 2. Vector Search
        query_vector = self.embedder.embed_text(query)
        vector_matches = self.vec_store.search_similar(query_vector, top_k=top_k * 2, active_only=True)

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        sources: Dict[str, str] = {}

        # Process BM25 ranks
        for rank, (node_id, _) in enumerate(bm25_matches, start=1):
            rrf_scores[node_id] = rrf_scores.get(node_id, 0.0) + (1.0 / (self.rrf_k + rank))
            sources[node_id] = "bm25"

        # Process Vector ranks
        for rank, match in enumerate(vector_matches, start=1):
            node_id = match["id"]
            rrf_scores[node_id] = rrf_scores.get(node_id, 0.0) + (1.0 / (self.rrf_k + rank))
            if node_id in sources:
                sources[node_id] = "hybrid"
            else:
                sources[node_id] = "vector"

        # Sort by final RRF score descending
        sorted_nodes = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)[:top_k]

        results: List[RetrievedMemory] = []
        for node_id, score in sorted_nodes:
            node = self.graph.get_node_by_id(node_id)
            if node and node.is_active:
                # Spaced repetition reinforcement
                self.graph.reinforce_node(node.id)
                results.append(
                    RetrievedMemory(
                        node=node,
                        score=score,
                        retrieval_source=sources.get(node_id, "hybrid"),
                    )
                )

        return results


hybrid_retriever = HybridRetriever()
