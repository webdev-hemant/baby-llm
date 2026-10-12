"""Unit tests for workspace-scoped memory isolation and retrieval."""

import pytest
from baby_llm.core.models import MemoryCategory, MemoryNode
from baby_llm.retrieval.hybrid import HybridRetriever
from baby_llm.storage.graph_store import BiTemporalGraphStore


def test_scoped_node_persistence_and_filtering(tmp_path):
    from baby_llm.storage.db import DatabaseManager
    db_file = tmp_path / "test_scoped.db"
    db = DatabaseManager(db_path=db_file)
    store = BiTemporalGraphStore(db=db)

    # 1. Insert global node
    n_global = MemoryNode(
        subject="user",
        predicate="prefers_theme",
        object="dark",
        category=MemoryCategory.PREFERENCE,
        scope="global",
    )
    store.insert_node(n_global)

    # 2. Insert repo-a node
    n_repo_a = MemoryNode(
        subject="project_a",
        predicate="uses_database",
        object="postgresql",
        category=MemoryCategory.WORK,
        scope="repo:project-a",
    )
    store.insert_node(n_repo_a)

    # 3. Insert repo-b node
    n_repo_b = MemoryNode(
        subject="project_b",
        predicate="uses_database",
        object="sqlite",
        category=MemoryCategory.WORK,
        scope="repo:project-b",
    )
    store.insert_node(n_repo_b)

    # Querying repo:project-a should return n_repo_a and n_global, but NOT n_repo_b
    nodes_a = store.get_active_nodes(scope="repo:project-a")
    ids_a = {n.id for n in nodes_a}
    assert n_repo_a.id in ids_a
    assert n_global.id in ids_a
    assert n_repo_b.id not in ids_a

    # Querying repo:project-b should return n_repo_b and n_global, but NOT n_repo_a
    nodes_b = store.get_active_nodes(scope="repo:project-b")
    ids_b = {n.id for n in nodes_b}
    assert n_repo_b.id in ids_b
    assert n_global.id in ids_b
    assert n_repo_a.id not in ids_b


def test_scoped_subgraph_traversal(tmp_path):
    from baby_llm.storage.db import DatabaseManager
    db_file = tmp_path / "test_subgraph.db"
    db = DatabaseManager(db_path=db_file)
    store = BiTemporalGraphStore(db=db)

    n1 = MemoryNode(
        subject="phoenix",
        predicate="uses_framework",
        object="fastapi",
        category=MemoryCategory.WORK,
        scope="repo:phoenix",
    )
    n2 = MemoryNode(
        subject="phoenix",
        predicate="target_port",
        object="21225",
        category=MemoryCategory.WORK,
        scope="repo:phoenix",
    )
    store.insert_node(n1)
    store.insert_node(n2)

    subgraph = store.get_entity_subgraph("phoenix", scope="repo:phoenix")
    assert len(subgraph) >= 2
    preds = {n.predicate for n in subgraph}
    assert "uses_framework" in preds
    assert "target_port" in preds
