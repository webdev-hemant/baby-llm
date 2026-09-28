"""Universal Model Context Protocol (MCP) Server for Baby LLM."""

import asyncio
from typing import List, Optional
from mcp.server.fastmcp import FastMCP
from baby_llm.core.models import MemoryCategory
from baby_llm.dream.resolver import conflict_resolver
from baby_llm.retrieval.hybrid import hybrid_retriever
from baby_llm.storage.graph_store import graph_store
from baby_llm.success.tracker import success_tracker

# Initialize FastMCP Server
mcp = FastMCP("baby-llm-mcp")


@mcp.tool()
def recall_memory(query: str, top_k: int = 5) -> str:
    """Retrieve verified personal context and memory nodes matching a query."""
    results = hybrid_retriever.retrieve(query, top_k=top_k)
    if not results:
        return "No relevant memories found."

    formatted = []
    for r in results:
        node = r.node
        formatted.append(
            f"- [{node.category.value.upper()}] {node.to_readable_fact()} "
            f"(Confidence: {int(node.confidence * 100)}%, Source: {r.retrieval_source})"
        )
    return "\n".join(formatted)


@mcp.tool()
def commit_fact(
    subject: str,
    predicate: str,
    object_: str,
    category: str = "preference",
    ymyl_protected: bool = False,
) -> str:
    """Explicitly commit or update a verified personal fact in the bi-temporal knowledge graph."""
    try:
        cat_enum = MemoryCategory(category.lower())
    except ValueError:
        cat_enum = MemoryCategory.PREFERENCE

    node = conflict_resolver.resolve_and_commit(
        subject=subject,
        predicate=predicate,
        object_=object_,
        category=cat_enum,
        confidence=1.0,
        ymyl_protected=ymyl_protected,
    )
    return f"Successfully committed memory node: {node.to_readable_fact()} (ID: {node.id})"


@mcp.tool()
def get_active_goals() -> str:
    """List active goals and commitments tracked by Baby LLM."""
    commitments = success_tracker.get_active_commitments()
    if not commitments:
        return "No active commitments found."

    lines = []
    for c in commitments:
        deadline = f" [Due: {c.target_deadline.strftime('%Y-%m-%d')}]" if c.target_deadline else ""
        lines.append(f"- [{c.status.value.upper()}] {c.title}{deadline}")
    return "\n".join(lines)


@mcp.tool()
def record_daily_win(note: str) -> str:
    """Record a win or accomplishment for the day."""
    conflict_resolver.resolve_and_commit(
        subject="user",
        predicate="accomplished",
        object_=note,
        category=MemoryCategory.GOAL,
        confidence=1.0,
    )
    return f"Recorded accomplishment: '{note}'"


def run_mcp_server() -> None:
    """Run standard stdio MCP server for Cursor & Claude Desktop."""
    mcp.run()


if __name__ == "__main__":
    run_mcp_server()
