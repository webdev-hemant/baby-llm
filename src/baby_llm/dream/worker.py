"""REM Dream Worker executing asynchronous memory consolidation."""

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from baby_llm.dream.decay import EbbinghausDecayEngine, decay_engine
from baby_llm.dream.extractor import FactExtractor, fact_extractor
from baby_llm.dream.resolver import ConflictResolver, conflict_resolver
from baby_llm.storage.wal import WriteAheadLog, wal_logger

logger = logging.getLogger(__name__)


class DreamWorker:
    def __init__(
        self,
        wal: WriteAheadLog = wal_logger,
        extractor: FactExtractor = fact_extractor,
        resolver: ConflictResolver = conflict_resolver,
        decay: EbbinghausDecayEngine = decay_engine,
        idle_threshold_seconds: float = 15 * 60,  # 15 minutes of inactivity default
    ):
        self.wal = wal
        self.extractor = extractor
        self.resolver = resolver
        self.decay = decay
        self.idle_threshold_seconds = idle_threshold_seconds

        # Concurrency & daemon management
        self._last_user_activity: float = time.time()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._lock = threading.Lock()
        self._daemon_thread: Optional[threading.Thread] = None
        self._last_cron_run_date: Optional[str] = None
        self._is_consolidating: bool = False

    def record_user_activity(self) -> None:
        """Notifies the worker of user activity; resets idle timer and temporarily pauses background consolidation."""
        with self._lock:
            self._last_user_activity = time.time()
        self.pause()
        # Resume after brief buffer to avoid competing for resources during user interaction
        threading.Timer(2.0, self.resume).start()

    def pause(self) -> None:
        """Immediately pauses background consolidation (e.g. while user is actively chatting)."""
        self._pause_event.set()

    def resume(self) -> None:
        """Resumes background consolidation."""
        self._pause_event.clear()

    @property
    def is_paused(self) -> bool:
        return self._pause_event.is_set()

    @property
    def is_running(self) -> bool:
        return self._daemon_thread is not None and self._daemon_thread.is_alive()

    def run_consolidation_cycle(self) -> Dict[str, Any]:
        """
        Executes a complete REM Dream consolidation cycle:
        1. Ingest unprocessed interaction turns from SQLite WAL.
        2. Extract atomic SPO facts with confidence and category tags.
        3. Perform Bi-temporal contradiction resolution & vector indexing.
        4. Recompute Ebbinghaus retention decay and prune expired trivia.
        """
        with self._lock:
            if self._is_consolidating:
                logger.info("Consolidation cycle already in progress; skipping.")
                return {"status": "in_progress"}
            self._is_consolidating = True

        try:
            unprocessed = self.wal.get_unprocessed_turns(limit=50)
            facts_extracted = 0
            processed_turn_ids = []

            for turn in unprocessed:
                # If paused by user activity during long batch, yield immediately
                if self._pause_event.is_set():
                    logger.info("Consolidation paused due to user activity.")
                    break

                extracted_triples = self.extractor.extract_from_turn(turn)
                for item in extracted_triples:
                    self.resolver.resolve_and_commit(
                        subject=item["subject"],
                        predicate=item["predicate"],
                        object_=item["object"],
                        category=item["category"],
                        confidence=item["confidence"],
                        ymyl_protected=item["ymyl"],
                        source_turn_id=turn.turn_id,
                    )
                    facts_extracted += 1

                processed_turn_ids.append(turn.turn_id)

            # Mark turns as consolidated
            if processed_turn_ids:
                self.wal.mark_turns_processed(processed_turn_ids)

            # Evaluate decay & prune
            archived_ids, surviving_ids = self.decay.evaluate_and_prune()

            summary = {
                "turns_processed": len(processed_turn_ids),
                "facts_extracted": facts_extracted,
                "nodes_archived": len(archived_ids),
                "active_nodes_count": len(surviving_ids),
            }
            logger.info(f"REM Dream Cycle complete: {summary}")
            return summary
        finally:
            with self._lock:
                self._is_consolidating = False

    def _daemon_loop(self, check_interval: float) -> None:
        """Background loop monitoring idle timeout and 03:00 AM nightly cron."""
        logger.info("REM Dream background daemon started.")
        while not self._stop_event.is_set():
            if self._stop_event.wait(timeout=check_interval):
                break

            if self._pause_event.is_set():
                continue

            now = datetime.now()
            today_str = now.strftime("%Y-%m-%d")

            # 1. Check 03:00 AM nightly consolidation window
            is_nightly_window = (now.hour == 3 and 0 <= now.minute < 30)
            if is_nightly_window and self._last_cron_run_date != today_str:
                logger.info("Triggering 03:00 AM nightly REM Dream consolidation.")
                self.run_consolidation_cycle()
                self._last_cron_run_date = today_str
                continue

            # 2. Check OS Idle Threshold
            with self._lock:
                idle_elapsed = time.time() - self._last_user_activity

            if idle_elapsed >= self.idle_threshold_seconds:
                unprocessed = self.wal.get_unprocessed_turns(limit=1)
                if unprocessed:
                    logger.info(
                        f"OS idle threshold reached ({idle_elapsed:.1f}s >= {self.idle_threshold_seconds}s). Consolidating..."
                    )
                    self.run_consolidation_cycle()

        logger.info("REM Dream background daemon stopped.")

    def start_background_daemon(
        self,
        idle_seconds: Optional[float] = None,
        check_interval: float = 1.0,
    ) -> None:
        """Starts the autonomous OS idle and 03:00 AM scheduler background thread."""
        if idle_seconds is not None:
            self.idle_threshold_seconds = idle_seconds

        if self.is_running:
            return

        self._stop_event.clear()
        self._pause_event.clear()
        self._daemon_thread = threading.Thread(
            target=self._daemon_loop,
            args=(check_interval,),
            name="REMDreamDaemon",
            daemon=True,
        )
        self._daemon_thread.start()

    def stop_background_daemon(self, timeout: float = 5.0) -> None:
        """Stops the autonomous background daemon thread gracefully."""
        self._stop_event.set()
        if self._daemon_thread and self._daemon_thread.is_alive():
            self._daemon_thread.join(timeout=timeout)
        self._daemon_thread = None


dream_worker = DreamWorker()
