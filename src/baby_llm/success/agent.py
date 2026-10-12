"""Proactive Success Agent: Morning Brief, Accountability Watchdog, Evening Reflection."""

from datetime import datetime, timezone
import logging
import threading
from typing import List, Optional
import uuid

from baby_llm.core.models import Commitment
from baby_llm.runtime.llm_provider import llm_provider
from baby_llm.storage.db import DatabaseManager, db_manager
from baby_llm.storage.graph_store import BiTemporalGraphStore, graph_store
from baby_llm.success.tracker import SuccessTracker, success_tracker

logger = logging.getLogger(__name__)


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

        # Scheduler daemon state
        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_morning_run_date: Optional[str] = None
        self._last_evening_run_date: Optional[str] = None
        self._lock = threading.Lock()

    def generate_morning_brief(self, force_refresh: bool = False) -> str:
        """Constructs 07:30 AM Morning Intention Brief with daily caching."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

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
        now = datetime.now(timezone.utc)
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

    def run_scheduled_tasks_now(self, brief_type: str = "morning") -> str:
        """Forces immediate execution of scheduled tasks for verification or manual triggers."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if brief_type == "morning":
            brief = self.generate_morning_brief(force_refresh=True)
            self._last_morning_run_date = today_str
            return brief
        elif brief_type == "evening":
            reflection = self.generate_evening_reflection()
            try:
                with self.db.get_connection() as conn:
                    conn.execute(
                        """
                        INSERT INTO daily_summaries (id, date, summary_type, content)
                        VALUES (?, ?, 'evening_reflection', ?)
                        ON CONFLICT(date) DO UPDATE SET content = excluded.content
                        """,
                        (str(uuid.uuid4()), today_str, reflection),
                    )
            except Exception:
                pass
            self._last_evening_run_date = today_str
            return reflection
        return ""

    def _scheduler_loop(self, check_interval: float) -> None:
        """Autonomous daemon loop checking 07:30 AM morning and 21:30 PM evening brief triggers."""
        logger.info("PersonalSuccessAgent scheduler daemon started.")
        while not self._stop_event.is_set():
            if self._stop_event.wait(timeout=check_interval):
                break

            now = datetime.now()
            today_str = now.strftime("%Y-%m-%d")

            # 1. Morning Brief (07:30 AM window)
            if now.hour == 7 and 30 <= now.minute < 45:
                if self._last_morning_run_date != today_str:
                    logger.info("Triggering autonomous 07:30 AM Morning Brief synthesis.")
                    self.generate_morning_brief(force_refresh=True)
                    self._last_morning_run_date = today_str

            # 2. Nightly Reflection (21:30 PM window)
            if now.hour == 21 and 30 <= now.minute < 45:
                if self._last_evening_run_date != today_str:
                    logger.info("Triggering autonomous 09:30 PM Nightly Reflection synthesis.")
                    reflection = self.generate_evening_reflection()
                    try:
                        with self.db.get_connection() as conn:
                            conn.execute(
                                """
                                INSERT INTO daily_summaries (id, date, summary_type, content)
                                VALUES (?, ?, 'evening_reflection', ?)
                                ON CONFLICT(date) DO UPDATE SET content = excluded.content
                                """,
                                (str(uuid.uuid4()), today_str, reflection),
                            )
                    except Exception:
                        pass
                    self._last_evening_run_date = today_str

        logger.info("PersonalSuccessAgent scheduler daemon stopped.")

    def start_scheduler(self, check_interval: float = 1.0) -> None:
        """Starts the autonomous morning/evening scheduler background thread."""
        with self._lock:
            if self.is_scheduler_running:
                return
            self._stop_event.clear()
            self._scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                args=(check_interval,),
                name="SuccessAgentScheduler",
                daemon=True,
            )
            self._scheduler_thread.start()

    def stop_scheduler(self, timeout: float = 2.0) -> None:
        """Stops the autonomous scheduler daemon thread gracefully."""
        self._stop_event.set()
        with self._lock:
            if self._scheduler_thread and self._scheduler_thread.is_alive():
                self._scheduler_thread.join(timeout=timeout)
            self._scheduler_thread = None

    @property
    def is_scheduler_running(self) -> bool:
        return self._scheduler_thread is not None and self._scheduler_thread.is_alive()


success_agent = PersonalSuccessAgent()
