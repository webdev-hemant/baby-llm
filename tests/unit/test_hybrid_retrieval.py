"""Unit tests for FTS5 BM25 and Hybrid Retrieval."""

import pytest
from baby_llm.core.models import MemoryCategory, MemoryNode
from baby_llm.retrieval.bm25 import BM25Retriever
from baby_llm.storage.db import DatabaseManager
from baby_llm.storage.graph_store import BiTemporalGraphStore


@pytest.fixture
def temp_environment(tmp_path):
    db_path = tmp_path / "test_bm25.sqlite3"
    db = DatabaseManager(db_path=db_path)
    graph = BiTemporalGraphStore(db=db)
    bm25 = BM25Retriever(db=db)
    return db, graph, bm25


def test_bm25_exact_match(temp_environment):
    db, graph, bm25 = temp_environment

    node1 = MemoryNode(
        subject="user",
        predicate="prefers",
        object="Dark Mode in IDE",
        category=MemoryCategory.PREFERENCE,
    )
    node2 = MemoryNode(
        subject="user",
        predicate="studies",
        object="Quantum Mechanics and Physics",
        category=MemoryCategory.GOAL,
    )
    graph.insert_node(node1)
    graph.insert_node(node2)

    results = bm25.search("Quantum Physics")
    assert len(results) >= 1
    assert results[0][0] == node2.id


def test_hybrid_retrieval_rrf(tmp_path):
    from baby_llm.retrieval.hybrid import HybridRetriever
    from baby_llm.storage.vector_store import LanceVectorStore

    db_path = tmp_path / "test_hybrid.sqlite3"
    db = DatabaseManager(db_path=db_path)
    graph = BiTemporalGraphStore(db=db)
    bm25 = BM25Retriever(db=db)
    vec_store = LanceVectorStore(db_path=tmp_path / "lancedb")

    class MockEmbedder:
        def embed_text(self, text: str):
            return [0.1] * 384

    retriever = HybridRetriever(
        embedder=MockEmbedder(),
        vec_store=vec_store,
        bm25=bm25,
        graph=graph,
    )

    node = MemoryNode(
        subject="user",
        predicate="enjoys",
        object="Rust and Python systems programming",
        category=MemoryCategory.PREFERENCE,
    )
    graph.insert_node(node)
    vec_store.upsert_node(node, [0.1] * 384)

    results = retriever.retrieve("Python programming", top_k=3)
    assert len(results) >= 1
    assert results[0].node.id == node.id
    assert results[0].retrieval_source in ("hybrid", "bm25", "vector")
