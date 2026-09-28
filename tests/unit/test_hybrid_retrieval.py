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
