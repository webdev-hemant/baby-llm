"""Integration test for REM Dream consolidation and contradiction resolution."""

import pytest
from baby_llm.core.models import InteractionTurn, MemoryCategory
from baby_llm.dream.decay import EbbinghausDecayEngine
from baby_llm.dream.extractor import FactExtractor
from baby_llm.dream.resolver import ConflictResolver
from baby_llm.dream.worker import DreamWorker
from baby_llm.storage.db import DatabaseManager
from baby_llm.storage.graph_store import BiTemporalGraphStore
from baby_llm.storage.vector_store import LanceVectorStore
from baby_llm.storage.wal import WriteAheadLog


@pytest.fixture
def integrated_system(tmp_path):
    db_path = tmp_path / "integrated.sqlite3"
    lance_path = tmp_path / "lancedb_test"
    db = DatabaseManager(db_path=db_path)
    wal = WriteAheadLog(db=db)
    graph = BiTemporalGraphStore(db=db)
    vec_store = LanceVectorStore(db_path=lance_path)
    resolver = ConflictResolver(graph=graph, vec_store=vec_store)
    decay = EbbinghausDecayEngine(graph=graph, vec_store=vec_store)
    extractor = FactExtractor()
    worker = DreamWorker(wal=wal, extractor=extractor, resolver=resolver, decay=decay)
    return wal, graph, worker, resolver


def test_full_dream_consolidation_and_contradiction(integrated_system):
    wal, graph, worker, resolver = integrated_system

    # Step 1: User says they live in London
    turn1 = InteractionTurn(
        user_input="I live in London and work remotely.",
        assistant_response="London is a vibrant city.",
    )
    wal.append_turn(turn1)

    # Run Dream cycle
    summary1 = worker.run_consolidation_cycle()
    assert summary1["turns_processed"] == 1
    assert summary1["facts_extracted"] >= 1

    active = graph.find_active_by_subject_predicate("user", "lives_in")
    assert len(active) == 1
    assert "london" in active[0].object.lower()

    # Step 2: Later, user moves to Tokyo (Contradiction / Update)
    turn2 = InteractionTurn(
        user_input="I live in Tokyo now after relocating.",
        assistant_response="Tokyo is a wonderful place to live.",
    )
    wal.append_turn(turn2)

    summary2 = worker.run_consolidation_cycle()
    assert summary2["turns_processed"] == 1

    # Check that Tokyo is active and London is archived
    active_now = graph.find_active_by_subject_predicate("user", "lives_in")
    assert len(active_now) == 1
    assert "tokyo" in active_now[0].object.lower()

    # Check complete history
    history = graph.get_history_for_subject_predicate("user", "lives_in")
    assert len(history) == 2
    assert "london" in history[0].object.lower()
    assert history[0].invalid_from is not None
    assert "tokyo" in history[1].object.lower()
    assert history[1].invalid_from is None


def test_dream_worker_background_daemon(tmp_path):
    import time

    class FastMockExtractor:
        def extract_from_turn(self, turn):
            return [{
                "subject": "user",
                "predicate": "reads",
                "object": "philosophy",
                "category": "preference",
                "confidence": 1.0,
                "ymyl": False,
            }]

    db_path = tmp_path / "daemon_test.sqlite3"
    lance_path = tmp_path / "lancedb_daemon"
    db = DatabaseManager(db_path=db_path)
    wal = WriteAheadLog(db=db)
    graph = BiTemporalGraphStore(db=db)
    vec_store = LanceVectorStore(db_path=lance_path)
    resolver = ConflictResolver(graph=graph, vec_store=vec_store)
    decay = EbbinghausDecayEngine(graph=graph, vec_store=vec_store)
    worker = DreamWorker(
        wal=wal,
        extractor=FastMockExtractor(),
        resolver=resolver,
        decay=decay,
    )

    # Verify daemon start and running state
    assert not worker.is_running
    worker.start_background_daemon(idle_seconds=0.05, check_interval=0.02)
    assert worker.is_running

    # Add a turn to WAL
    turn = InteractionTurn(
        user_input="I prefer reading books on philosophy.",
        assistant_response="Philosophy offers profound perspectives.",
    )
    wal.append_turn(turn)
    assert len(wal.get_unprocessed_turns()) == 1

    # Wait for idle timeout (0.05s) to trigger consolidation
    for _ in range(30):
        if len(wal.get_unprocessed_turns()) == 0:
            break
        time.sleep(0.02)

    assert len(wal.get_unprocessed_turns()) == 0

    # Test user activity pause mechanism
    worker.record_user_activity()
    assert worker.is_paused

    # Stop daemon gracefully
    worker.stop_background_daemon(timeout=2.0)
    assert not worker.is_running
