"""Local Embedded LLM Provider: 100% self-contained inference using llama-cpp-python."""

import logging
from typing import Generator, List, Optional
from baby_llm.runtime.embedded_engine import EmbeddedLLMEngine, embedded_engine

logger = logging.getLogger(__name__)


class LocalLLMProvider:
    """
    Direct embedded LLM provider running Qwen2.5-0.5B-Instruct locally.
    Fully independent of Ollama and external daemon services.
    """

    def __init__(self, engine: Optional[EmbeddedLLMEngine] = None, **kwargs):
        self.engine = engine or embedded_engine

    def chat_sync(
        self,
        messages: List[dict],
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """
        Executes synchronous chat completion directly via the embedded llama-cpp engine.
        Zero external daemons or services required.
        """
        return self.engine.chat_sync(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def stream_chat(
        self,
        messages: List[dict],
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> Generator[str, None, None]:
        """Stream tokens directly from embedded llama-cpp engine."""
        return self.engine.stream_chat_sync(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )


# Backward-compatible aliases
UnifiedLLMProvider = LocalLLMProvider
llm_provider = LocalLLMProvider()
