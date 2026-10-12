"""Commitments and goals state-machine tracker."""

from datetime import datetime, timezone
from typing import List, Optional
from baby_llm.core.models import Commitment, CommitmentStatus
from baby_llm.storage.db import DatabaseManager, db_manager


class SuccessTracker:
    def __init__(self, db: DatabaseManager = db_manager):
        self.db = db

    def add_commitment(
        self,
        title: str,
        description: Optional[str] = None,
        target_deadline: Optional[datetime] = None,
        associated_node_id: Optional[str] = None,
    ) -> Commitment:
        commitment = Commitment(
            title=title,
            description=description,
            status=CommitmentStatus.PENDING,
            target_deadline=target_deadline,
            associated_node_id=associated_node_id,
        )
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO commitments (
                    id, title, description, status, target_deadline,
                    detected_at, resolved_at, associated_node_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    commitment.id,
                    commitment.title,
                    commitment.description,
                    commitment.status.value,
                    commitment.target_deadline.isoformat() if commitment.target_deadline else None,
                    commitment.detected_at.isoformat(),
                    None,
                    commitment.associated_node_id,
                ),
            )
        return commitment

    def update_status(self, commitment_id: str, new_status: CommitmentStatus) -> bool:
        resolved_at = datetime.now(timezone.utc).isoformat() if new_status in (CommitmentStatus.COMPLETED, CommitmentStatus.DROPPED) else None
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE commitments
                SET status = ?, resolved_at = ?
                WHERE id = ?
                """,
                (new_status.value, resolved_at, commitment_id),
            )
            return cursor.rowcount > 0

    def get_active_commitments(self) -> List[Commitment]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM commitments
                WHERE status IN ('pending', 'in_progress')
                ORDER BY target_deadline ASC NULLS LAST
                """
            )
            return [self._row_to_commitment(r) for r in cursor.fetchall()]

    def _row_to_commitment(self, row) -> Commitment:
        return Commitment(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=CommitmentStatus(row["status"]),
            target_deadline=datetime.fromisoformat(row["target_deadline"]) if row["target_deadline"] else None,
            detected_at=datetime.fromisoformat(row["detected_at"]),
            resolved_at=datetime.fromisoformat(row["resolved_at"]) if row["resolved_at"] else None,
            associated_node_id=row["associated_node_id"],
        )


success_tracker = SuccessTracker()
