"""Unit tests for PersonalSuccessAgent morning brief, overdue watchdog, and autonomous scheduler."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
from unittest.mock import MagicMock

from baby_llm.storage.db import DatabaseManager
from baby_llm.storage.graph_store import BiTemporalGraphStore
from baby_llm.success.agent import PersonalSuccessAgent
from baby_llm.success.tracker import SuccessTracker


def test_morning_brief_and_daily_caching():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(db_path=Path(tmpdir) / "test_agent.db")
        tracker = SuccessTracker(db=db)
        graph = BiTemporalGraphStore(db=db)

        # Mock LLM provider for air-gapped test speed
        mock_llm = MagicMock()
        mock_llm.chat_sync.return_value = "🌅 Mock Morning Brief: Focus on deep work."

        agent = PersonalSuccessAgent(tracker=tracker, graph=graph, db=db, llm=mock_llm)

        # 1. Add commitment
        tracker.add_commitment("Complete Architecture Design", "Finish M4 review")

        # 2. First generation invokes LLM
        brief1 = agent.generate_morning_brief()
        assert "Mock Morning Brief" in brief1
        assert mock_llm.chat_sync.call_count == 1

        # 3. Second call uses SQLite cache without re-invoking LLM
        brief2 = agent.generate_morning_brief()
        assert brief2 == brief1
        assert mock_llm.chat_sync.call_count == 1  # Still 1, served from cache!

        # 4. Force refresh bypasses cache
        brief3 = agent.generate_morning_brief(force_refresh=True)
        assert mock_llm.chat_sync.call_count == 2


def test_overdue_commitments_watchdog():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(db_path=Path(tmpdir) / "test_watchdog.db")
        tracker = SuccessTracker(db=db)
        agent = PersonalSuccessAgent(tracker=tracker, db=db)

        # Add commitment due 3 days in the past
        past_deadline = datetime.now(timezone.utc) - timedelta(days=3)
        tracker.add_commitment(
            title="Submit Tax Documents",
            target_deadline=past_deadline,
        )

        # Add commitment due tomorrow
        future_deadline = datetime.now(timezone.utc) + timedelta(days=1)
        tracker.add_commitment(
            title="Team Standup",
            target_deadline=future_deadline,
        )

        alerts = agent.check_overdue_commitments()
        assert len(alerts) == 1
        assert "Submit Tax Documents" in alerts[0]
        assert "day(s) ago" in alerts[0]


def test_evening_reflection():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(db_path=Path(tmpdir) / "test_evening.db")
        mock_llm = MagicMock()
        mock_llm.chat_sync.return_value = "🌙 Great reflection: You crushed your milestones today."
        agent = PersonalSuccessAgent(db=db, llm=mock_llm)

        res = agent.generate_evening_reflection("Had a productive coding session.")
        assert "Great reflection" in res
        assert mock_llm.chat_sync.called


def test_autonomous_scheduler_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(db_path=Path(tmpdir) / "test_sched.db")
        agent = PersonalSuccessAgent(db=db)

        assert agent.is_scheduler_running is False
        agent.start_scheduler(check_interval=0.1)
        assert agent.is_scheduler_running is True

        # Test immediate execution hook
        morning_res = agent.run_scheduled_tasks_now("morning")
        assert len(morning_res) > 0
        evening_res = agent.run_scheduled_tasks_now("evening")
        assert len(evening_res) > 0

        agent.stop_scheduler()
        assert agent.is_scheduler_running is False
