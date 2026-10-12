"""Unit tests for Architectural Invariant Guardrail Engine."""

from unittest.mock import MagicMock
from baby_llm.core.guardrail import InvariantGuardrail
from baby_llm.core.models import MemoryCategory, MemoryNode, RetrievedMemory


def test_guardrail_detects_prohibition_violation():
    mock_retriever = MagicMock()
    mock_provider = MagicMock()

    # Conflicting node: user strictly avoids tailwindcss
    conflicting_node = MemoryNode(
        subject="user",
        predicate="strictly avoids tailwindcss",
        object="TailwindCSS",
        category=MemoryCategory.WORK,
        scope="repo:test",
    )
    mock_retriever.retrieve.return_value = [
        RetrievedMemory(node=conflicting_node, score=0.95, retrieval_source="hybrid")
    ]

    guard = InvariantGuardrail(retriever=mock_retriever, provider=mock_provider)
    report = guard.check_proposal("Install tailwindcss and setup config", scope="repo:test")

    assert "⚠️ INVARIANT VIOLATION DETECTED" in report
    assert "tailwindcss" in report.lower()
    assert "Recommendation" in report


def test_guardrail_passes_clean_proposal():
    mock_retriever = MagicMock()
    mock_provider = MagicMock()
    mock_provider.chat_sync.return_value = "OK"

    # Safe node: user prefers vanilla css
    safe_node = MemoryNode(
        subject="user",
        predicate="prefers_styling",
        object="vanilla_css",
        category=MemoryCategory.WORK,
        scope="repo:test",
    )
    mock_retriever.retrieve.return_value = [
        RetrievedMemory(node=safe_node, score=0.90, retrieval_source="bm25")
    ]

    guard = InvariantGuardrail(retriever=mock_retriever, provider=mock_provider)
    report = guard.check_proposal("Update index.html layout styling with standard flexbox", scope="repo:test")

    assert "✅ PASSED" in report
    assert "Active Context Considered" in report


def test_guardrail_empty_proposal():
    guard = InvariantGuardrail()
    report = guard.check_proposal("   ")
    assert "Empty proposal provided" in report
