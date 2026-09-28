"""In-memory episodic ring buffer for low-latency recent context."""

from collections import deque
from typing import List
from baby_llm.core.models import InteractionTurn


class EpisodicRingBuffer:
    def __init__(self, max_size: int = 15):
        self.max_size = max_size
        self._buffer: deque[InteractionTurn] = deque(maxlen=max_size)

    def append(self, turn: InteractionTurn) -> None:
        self._buffer.append(turn)

    def get_recent_turns(self, n: int | None = None) -> List[InteractionTurn]:
        turns = list(self._buffer)
        if n is not None and n > 0:
            return turns[-n:]
        return turns

    def clear(self) -> None:
        self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)
