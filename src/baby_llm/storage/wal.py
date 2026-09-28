"""Write-Ahead Interaction Logger (WAL) for conversational turns."""

from typing import List, Optional
from baby_llm.core.models import InteractionTurn
from baby_llm.storage.db import DatabaseManager, db_manager


class WriteAheadLog:
    def __init__(self, db: DatabaseManager = db_manager):
        self.db = db

    def append_turn(self, turn: InteractionTurn) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO interaction_log (
                    turn_id, session_id, timestamp, user_input,
                    assistant_response, sentiment_tag, processed_in_dream
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    turn.turn_id,
                    turn.session_id,
                    turn.timestamp.isoformat(),
                    turn.user_input,
                    turn.assistant_response,
                    turn.sentiment_tag,
                    1 if turn.processed_in_dream else 0,
                ),
            )

    def get_unprocessed_turns(self, limit: int = 100) -> List[InteractionTurn]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT turn_id, session_id, timestamp, user_input,
                       assistant_response, sentiment_tag, processed_in_dream
                FROM interaction_log
                WHERE processed_in_dream = 0
                ORDER BY timestamp ASC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [
                InteractionTurn(
                    turn_id=row["turn_id"],
                    session_id=row["session_id"],
                    timestamp=row["timestamp"],
                    user_input=row["user_input"],
                    assistant_response=row["assistant_response"],
                    sentiment_tag=row["sentiment_tag"],
                    processed_in_dream=bool(row["processed_in_dream"]),
                )
                for row in rows
            ]

    def mark_turns_processed(self, turn_ids: List[str]) -> None:
        if not turn_ids:
            return
        placeholders = ",".join("?" for _ in turn_ids)
        with self.db.get_connection() as conn:
            conn.execute(
                f"UPDATE interaction_log SET processed_in_dream = 1 WHERE turn_id IN ({placeholders})",
                turn_ids,
            )

    def get_recent_turns(self, limit: int = 15) -> List[InteractionTurn]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT turn_id, session_id, timestamp, user_input,
                       assistant_response, sentiment_tag, processed_in_dream
                FROM interaction_log
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            turns = [
                InteractionTurn(
                    turn_id=row["turn_id"],
                    session_id=row["session_id"],
                    timestamp=row["timestamp"],
                    user_input=row["user_input"],
                    assistant_response=row["assistant_response"],
                    sentiment_tag=row["sentiment_tag"],
                    processed_in_dream=bool(row["processed_in_dream"]),
                )
                for row in rows
            ]
            turns.reverse()
            return turns


wal_logger = WriteAheadLog()
