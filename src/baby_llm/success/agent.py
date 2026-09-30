"""Proactive Success Agent: Morning Brief, Accountability Watchdog, Evening Reflection."""

from datetime import datetime
from typing import List
from baby_llm.core.models import Commitment
from baby_llm.runtime.llm_provider import llm_provider
from baby_llm.storage.db import DatabaseManager, db_manager
from baby_llm.storage.graph_store import BiTemporalGraphStore, graph_store
from baby_llm.success.tracker import SuccessTracker, success_tracker
import uuid


class PersonalSuccessAgent:
    def __init__(
        self,
        tracker: SuccessTracker = success_tracker,
        graph: BiTemporalGraphStore = graph_store,
        db: DatabaseManager = db_manager,
        llm = llm_provider,
    ):
        self.tracker = tracker
        self.graph = graph
        self.db = db
        self.llm = llm

    def generate_morning_brief(self, force_refresh: bool = False) -> str:
        """Constructs 07:30 AM Morning Intention Brief with daily caching."""
        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        if not force_refresh:
            try:
                with self.db.get_connection() as conn:
                    cursor = conn.execute(
                        "SELECT content FROM daily_summaries WHERE date = ? AND summary_type = 'morning_brief'",
                        (today_str,),
                    )
                    row = cursor.fetchone()
                    if row:
                        return row["content"]
            except Exception:
                pass

        commitments: List[Commitment] = self.tracker.get_active_commitments()
        prompt_context = []
        if commitments:
            prompt_context.append("Open Commitments:\n" + "\n".join(f"- {c.title}" for c in commitments[:5]))

        prompt = (
            "You are Baby LLM, a personal success companion. Synthesize a concise 3-bullet "
            "'Morning Readiness Brief' for the user. Highlight top needle-moving priorities "
            "and offer brief, empowering focus guidance.\n\n"
            + "\n".join(prompt_context)
        )

        try:
            brief_content = self.llm.chat_sync([{"role": "user", "content": prompt}])
        except Exception:
            items = [f"• Priority: {c.title}" for c in commitments[:2]]
            if not items:
                items = ["• Define your top 2 needle-moving priorities for today."]
            brief_content = (
                "🌅 **Good morning! Here is your Morning Readiness Brief:**\n"
                + "\n".join(items)
                + "\n• Maintain focus and protect your deep-work windows."
            )

        # Cache in daily_summaries
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO daily_summaries (id, date, summary_type, content)
                    VALUES (?, ?, 'morning_brief', ?)
                    ON CONFLICT(date) DO UPDATE SET content = excluded.content
                    """,
                    (str(uuid.uuid4()), today_str, brief_content),
                )
        except Exception:
            pass

        return brief_content

    def check_overdue_commitments(self) -> List[str]:
        """Accountability Watchdog identifying dropped or overdue deadlines."""
        now = datetime.utcnow()
        active = self.tracker.get_active_commitments()
        alerts = []
        for c in active:
            if c.target_deadline and c.target_deadline < now:
                days_overdue = (now - c.target_deadline).days
                alerts.append(f"Commitment '{c.title}' was due {days_overdue} day(s) ago.")
        return alerts

    def generate_evening_reflection(self, brain_dump: str = "") -> str:
        """Constructs 09:30 PM Nightly Reflection."""
        prompt = (
            f"The user wrote this evening reflection note: '{brain_dump}'. "
            "Acknowledge wins, validate any friction points, and provide an encouraging, "
            "calming close to help them unwind and clear their mental runway."
        )
        try:
            return self.llm.chat_sync([{"role": "user", "content": prompt}])
        except Exception:
            return (
                "🌙 **Nightly Reflection Recorded.**\n"
                "Great work navigating today's challenges. Rest well and recharge for tomorrow."
            )


success_agent = PersonalSuccessAgent()
