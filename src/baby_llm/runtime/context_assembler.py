"""Fast-Path Context Assembler for real-time prompt generation (<20ms)."""

from typing import List, Optional
from baby_llm.core.models import InteractionTurn, RetrievedMemory
from baby_llm.core.ring_buffer import EpisodicRingBuffer
from baby_llm.retrieval.hybrid import HybridRetriever, hybrid_retriever
from baby_llm.storage.db import DatabaseManager, db_manager


BASE_PERSONA_PROMPT = """You are Baby LLM, an evolving, privacy-first personal companion and life success manager.
You operate completely locally on the user's device.
Tone: Warm, intelligent, highly attentive, honest, concise, and focused on helping the user succeed.
Never hallucinate user facts. If you know personal context from your memory, incorporate it naturally.
"""


class ContextAssembler:
    def __init__(
        self,
        retriever: HybridRetriever = hybrid_retriever,
        db: DatabaseManager = db_manager,
    ):
        self.retriever = retriever
        self.db = db

    def assemble(
        self,
        user_input: str,
        ring_buffer: EpisodicRingBuffer,
        include_memories: bool = True,
    ) -> List[dict]:
        """
        Compiles the full message payload for local LLM inference.
        Returns a list of OpenAI/Ollama compatible chat messages:
        [{"role": "system", "content": "..."}, {"role": "user", ...}]
        """
        system_sections = [BASE_PERSONA_PROMPT.strip()]

        # 1. Retrieve Active Long-Term Memories
        if include_memories:
            retrieved = self.retriever.retrieve(user_input, top_k=5)
            if retrieved:
                memory_lines = ["\n[Verified Personal Context & Memories]:"]
                for item in retrieved:
                    node = item.node
                    memory_lines.append(f"- {node.to_readable_fact()} (Category: {node.category.value})")
                system_sections.append("\n".join(memory_lines))

        # 2. Retrieve Active Open Commitments
        active_commitments = self._get_active_commitments()
        if active_commitments:
            commit_lines = ["\n[Active User Goals & Commitments]:"]
            for c in active_commitments:
                deadline = f" (Deadline: {c['deadline']})" if c['deadline'] else ""
                commit_lines.append(f"- {c['title']}{deadline}")
            system_sections.append("\n".join(commit_lines))

        messages = [{"role": "system", "content": "\n\n".join(system_sections)}]

        # 3. Add Episodic Recent Turns from Ring Buffer
        recent_turns: List[InteractionTurn] = ring_buffer.get_recent_turns()
        for turn in recent_turns:
            messages.append({"role": "user", "content": turn.user_input})
            messages.append({"role": "assistant", "content": turn.assistant_response})

        # 4. Current User Turn
        messages.append({"role": "user", "content": user_input})

        return messages

    def _get_active_commitments(self, limit: int = 5) -> List[dict]:
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT title, target_deadline
                    FROM commitments
                    WHERE status IN ('pending', 'in_progress')
                    ORDER BY target_deadline ASC NULLS LAST
                    LIMIT ?
                    """,
                    (limit,),
                )
                return [{"title": r["title"], "deadline": r["target_deadline"]} for r in cursor.fetchall()]
        except Exception:
            return []


context_assembler = ContextAssembler()
