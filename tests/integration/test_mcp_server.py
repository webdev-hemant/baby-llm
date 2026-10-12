"""Integration tests for Universal Model Context Protocol (MCP) server tools."""

import pytest
from baby_llm.mcp.server import commit_fact, get_active_goals, recall_memory, record_daily_win
from baby_llm.storage.graph_store import graph_store
from baby_llm.success.tracker import success_tracker


def test_mcp_commit_fact_and_recall():
    # 1. Commit a fact via MCP tool
    commit_res = commit_fact(
        subject="user",
        predicate="enjoys_reading",
        object_="Marcus Aurelius Meditations",
        category="preference",
        ymyl_protected=False,
    )
    assert "Successfully committed memory node" in commit_res
    assert "Marcus Aurelius Meditations" in commit_res

    # 2. Recall memory via MCP tool
    recall_res = recall_memory(query="Marcus Aurelius Meditations", top_k=3)
    assert "Marcus Aurelius Meditations" in recall_res
    assert "[PREFERENCE]" in recall_res


def test_mcp_goals_and_daily_win():
    # 1. Record a daily win via MCP tool
    win_note = "Finished Milestone 3 Glass-Box UI and MCP server implementation"
    win_res = record_daily_win(note=win_note)
    assert "Recorded accomplishment" in win_res
    assert win_note in win_res

    # 2. Add an active goal commitment and retrieve via MCP tool
    success_tracker.add_commitment(
        title="Deploy Baby LLM Glass-Box dashboard locally",
        description="Verify port 21225 and PWA standalone launcher",
    )
    goals_res = get_active_goals()
    assert "Deploy Baby LLM Glass-Box dashboard locally" in goals_res
    assert "[PENDING]" in goals_res
