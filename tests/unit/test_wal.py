"""Unit tests for Write-Ahead Interaction Logger (WAL)."""

import pytest
from baby_llm.core.models import InteractionTurn
from baby_llm.storage.db import DatabaseManager
from baby_llm.storage.wal import WriteAheadLog


@pytest.fixture
def temp_wal(tmp_path):
    db_path = tmp_path / "test_wal.sqlite3"
    db = DatabaseManager(db_path=db_path)
    return WriteAheadLog(db=db)


def test_append_and_retrieve_turn(temp_wal):
    turn = InteractionTurn(
        user_input="I love hiking on Mount Rainier.",
        assistant_response="That sounds exhilarating!",
    )
    temp_wal.append_turn(turn)

    unprocessed = temp_wal.get_unprocessed_turns()
    assert len(unprocessed) == 1
    assert unprocessed[0].turn_id == turn.turn_id
    assert unprocessed[0].user_input == "I love hiking on Mount Rainier."
    assert not unprocessed[0].processed_in_dream


def test_mark_turns_processed(temp_wal):
    turn = InteractionTurn(
        user_input="I drink green tea every morning.",
        assistant_response="A healthy routine.",
    )
    temp_wal.append_turn(turn)

    temp_wal.mark_turns_processed([turn.turn_id])
    unprocessed = temp_wal.get_unprocessed_turns()
    assert len(unprocessed) == 0

    recent = temp_wal.get_recent_turns(limit=5)
    assert len(recent) == 1
    assert recent[0].processed_in_dream is True
