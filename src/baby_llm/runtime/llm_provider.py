"""Unified LLM Provider: Seamlessly switches between Embedded Qwen2.5-0.5B and Ollama."""

import logging
from typing import AsyncGenerator, List, Optional
from baby_llm.runtime.embedded_engine import embedded_engine
from baby_llm.runtime.ollama_client import ollama_client

logger = logging.getLogger(__name__)


class UnifiedLLMProvider:
    def __init__(self, prefer_embedded: bool = True):
        self.prefer_embedded = prefer_embedded

    def chat_sync(self, messages: List[dict]) -> str:
        """
        Attempts inference using Embedded Qwen2.5-0.5B first (zero daemon required).
        Falls back to Ollama if explicitly preferred or available.
        """
        if self.prefer_embedded:
            try:
                return embedded_engine.chat_sync(messages)
            except Exception as e:
                logger.warning(f"Embedded engine error: {e}. Trying Ollama...")
                try:
                    return ollama_client.chat_sync(messages)
                except Exception:
                    raise e
        else:
            try:
                return ollama_client.chat_sync(messages)
            except Exception:
                logger.info("Ollama unreachable. Falling back to embedded Qwen2.5-0.5B...")
                return embedded_engine.chat_sync(messages)


llm_provider = UnifiedLLMProvider(prefer_embedded=True)
