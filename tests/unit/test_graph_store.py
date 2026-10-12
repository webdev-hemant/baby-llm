"""Unit tests for Bi-Temporal Graph Store."""

from datetime import datetime, timedelta, timezone
import pytest
from baby_llm.core.models import MemoryCategory, MemoryNode
from baby_llm.storage.db import DatabaseManager
from baby_llm.storage.graph_store import BiTemporalGraphStore


@pytest.fixture
def temp_graph(tmp_path):
    db_path = tmp_path / "test_graph.sqlite3"
    db = DatabaseManager(db_path=db_path)
    return BiTemporalGraphStore(db=db)


def test_insert_and_active_lookup(temp_graph):
    node = MemoryNode(
        subject="user",
        predicate="lives_in",
        object="Seattle",
        category=MemoryCategory.LIFESTYLE,
    )
    temp_graph.insert_node(node)

    active = temp_graph.find_active_by_subject_predicate("user", "lives_in")
    assert len(active) == 1
    assert active[0].object == "Seattle"
    assert active[0].is_active is True


def test_bi_temporal_invalidation_and_history(temp_graph):
    # 1. Insert original node (lived in Seattle)
    node1 = MemoryNode(
        subject="user",
        predicate="lives_in",
        object="Seattle",
        category=MemoryCategory.LIFESTYLE,
        valid_from=datetime.now(timezone.utc) - timedelta(days=365),
    )
    temp_graph.insert_node(node1)

    # 2. Invalidate node1 when user moves to Austin
    move_date = datetime.now(timezone.utc)
    temp_graph.invalidate_node(node1.id, invalid_time=move_date)

    node2 = MemoryNode(
        subject="user",
        predicate="lives_in",
        object="Austin",
        category=MemoryCategory.LIFESTYLE,
        valid_from=move_date,
    )
    temp_graph.insert_node(node2)

    # 3. Check active state
    active = temp_graph.find_active_by_subject_predicate("user", "lives_in")
    assert len(active) == 1
    assert active[0].object == "Austin"

    # 4. Check historical trajectory
    history = temp_graph.get_history_for_subject_predicate("user", "lives_in")
    assert len(history) == 2
    assert history[0].object == "Seattle"
    assert history[0].invalid_from is not None
    assert history[1].object == "Austin"
    assert history[1].invalid_from is None


def test_reinforce_node(temp_graph):
    node = MemoryNode(
        subject="user",
        predicate="drinks",
        object="espresso",
        stability=1.0,
    )
    temp_graph.insert_node(node)
    temp_graph.reinforce_node(node.id)

    fetched = temp_graph.get_node_by_id(node.id)
    assert fetched.stability == 2.0
