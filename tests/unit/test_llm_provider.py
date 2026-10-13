"""Unit tests for standalone embedded LLM provider."""

from unittest.mock import MagicMock
import pytest

from baby_llm.runtime.llm_provider import LocalLLMProvider, UnifiedLLMProvider, llm_provider
from baby_llm.config import settings


def test_llm_provider_embedded_chat():
    """Verify LocalLLMProvider dispatches chat_sync directly to embedded engine."""
    mock_engine = MagicMock()
    mock_engine.chat_sync.return_value = "Hello from embedded model"
    
    provider = LocalLLMProvider(engine=mock_engine)
    messages = [{"role": "user", "content": "Hi"}]
    
    result = provider.chat_sync(messages, max_tokens=100, temperature=0.5)
    assert result == "Hello from embedded model"
    mock_engine.chat_sync.assert_called_once_with(
        messages=messages,
        max_tokens=100,
        temperature=0.5,
    )


def test_llm_provider_embedded_stream():
    """Verify LocalLLMProvider streams directly from embedded engine."""
    mock_engine = MagicMock()
    mock_engine.stream_chat_sync.return_value = iter(["Hello", " world"])
    
    provider = LocalLLMProvider(engine=mock_engine)
    messages = [{"role": "user", "content": "Hi"}]
    
    chunks = list(provider.stream_chat(messages, max_tokens=100, temperature=0.5))
    assert chunks == ["Hello", " world"]
    mock_engine.stream_chat_sync.assert_called_once_with(
        messages=messages,
        max_tokens=100,
        temperature=0.5,
    )


def test_unified_provider_alias():
    """Verify UnifiedLLMProvider is aliased to LocalLLMProvider for backward compatibility."""
    assert UnifiedLLMProvider is LocalLLMProvider
    assert isinstance(llm_provider, LocalLLMProvider)


def test_config_embedded_settings():
    """Verify settings configure embedded engine without Ollama requirements."""
    assert hasattr(settings, "embedded_model_repo")
    assert hasattr(settings, "embedded_model_filename")
    assert settings.embedded_model_repo == "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
    assert settings.embedded_model_filename == "qwen2.5-0.5b-instruct-q4_k_m.gguf"
    # Ensure Ollama settings are completely absent
    assert not hasattr(settings, "ollama_base_url")
