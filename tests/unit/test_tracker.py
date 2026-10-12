"""Unit tests for SuccessTracker commitment state-machine."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
from baby_llm.core.models import CommitmentStatus
from baby_llm.storage.db import DatabaseManager
from baby_llm.success.tracker import SuccessTracker


def test_commitment_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(db_path=Path(tmpdir) / "test_tracker.db")
        tracker = SuccessTracker(db=db)

        # 1. Add commitment
        deadline = datetime.now(timezone.utc) + timedelta(days=2)
        c = tracker.add_commitment(
            title="Ship Milestone 4 Verification Suite",
            description="Complete all unit and integration tests",
            target_deadline=deadline,
        )
        assert c.id is not None
        assert c.title == "Ship Milestone 4 Verification Suite"
        assert c.status == CommitmentStatus.PENDING

        # 2. Get active commitments
        active = tracker.get_active_commitments()
        assert len(active) == 1
        assert active[0].id == c.id

        # 3. Transition to IN_PROGRESS
        updated = tracker.update_status(c.id, CommitmentStatus.IN_PROGRESS)
        assert updated is True
        active_after = tracker.get_active_commitments()
        assert active_after[0].status == CommitmentStatus.IN_PROGRESS

        # 4. Complete commitment (should clear from active)
        completed = tracker.update_status(c.id, CommitmentStatus.COMPLETED)
        assert completed is True
        active_final = tracker.get_active_commitments()
        assert len(active_final) == 0
