"""Integration tests for extended MCP tools, scoping, and guardrail checking."""

import pytest
from baby_llm.mcp.server import (
    get_entity_subgraph,
    get_goals_resource,
    get_scope_rules_resource,
    recall_memory,
    remember,
    verify_against_memory,
)


def test_mcp_remember_and_scoped_recall():
    # 1. Natural language remember in repo-scoped context
    res = remember(
        text="The team enforces FastAPI and strictly forbids Django",
        category="work",
        scope="repo:phoenix-api",
    )
    assert "Successfully remembered" in res

    # 2. Scoped recall inside repo:phoenix-api
    recall_res = recall_memory(
        query="Django",
        scope="repo:phoenix-api",
        top_k=3,
    )
    assert "django" in recall_res.lower()

    # 3. Guardrail violation check
    warn_res = verify_against_memory(
        proposal="Migrate our endpoints to Django REST framework",
        scope="repo:phoenix-api",
    )
    assert "⚠️ INVARIANT VIOLATION DETECTED" in warn_res
    assert "django" in warn_res.lower()

    # 4. Guardrail pass check
    pass_res = verify_against_memory(
        proposal="Add a new health check endpoint to FastAPI server",
        scope="repo:phoenix-api",
    )
    assert "✅ PASSED" in pass_res


def test_mcp_subgraph_and_resources():
    # 1. Test get_entity_subgraph
    subgraph = get_entity_subgraph("user", scope="global")
    assert "Knowledge Subgraph" in subgraph

    # 2. Test get_scope_rules_resource
    rules = get_scope_rules_resource("repo:phoenix-api")
    assert "Architectural Rules" in rules

    # 3. Test get_goals_resource
    goals = get_goals_resource()
    assert "Active Goals" in goals
