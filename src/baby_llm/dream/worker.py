"""REM Dream Worker executing asynchronous memory consolidation."""

import logging
from typing import Dict, Any
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
    ):
        self.wal = wal
        self.extractor = extractor
        self.resolver = resolver
        self.decay = decay

    def run_consolidation_cycle(self) -> Dict[str, Any]:
        """
        Executes a complete REM Dream consolidation cycle:
        1. Ingest unprocessed interaction turns from SQLite WAL.
        2. Extract atomic SPO facts with confidence and category tags.
        3. Perform Bi-temporal contradiction resolution & vector indexing.
        4. Recompute Ebbinghaus retention decay and prune expired trivia.
        """
        unprocessed = self.wal.get_unprocessed_turns(limit=50)
        facts_extracted = 0
        conflicts_resolved = 0
        processed_turn_ids = []

        for turn in unprocessed:
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


dream_worker = DreamWorker()
