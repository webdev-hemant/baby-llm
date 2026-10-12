"""Universal Model Context Protocol (MCP) Server for Baby LLM."""

import asyncio
from typing import List, Optional

try:
    from mcp.server.fastmcp import FastMCP
except (ImportError, ModuleNotFoundError):
    try:
        from mcp.server.mcpserver import MCPServer as FastMCP
    except (ImportError, ModuleNotFoundError):
        FastMCP = None

from baby_llm.core.guardrail import guardrail
from baby_llm.core.models import MemoryCategory
from baby_llm.dream.extractor import fact_extractor
from baby_llm.dream.resolver import conflict_resolver
from baby_llm.retrieval.hybrid import hybrid_retriever
from baby_llm.storage.graph_store import graph_store
from baby_llm.success.tracker import success_tracker

# Initialize FastMCP Server
mcp = FastMCP("baby-llm-mcp") if FastMCP is not None else None


@mcp.tool()
def remember(
    text: str,
    category: str = "work",
    scope: str = "global",
) -> str:
    """
    Zero-friction natural language memory ingestion for AI agents.
    Accepts raw statements without requiring rigid Subject-Predicate-Object decomposition.
    """
    clean_text = text.strip()
    if not clean_text:
        return "No text provided to remember."

    try:
        cat_enum = MemoryCategory(category.lower())
    except ValueError:
        cat_enum = MemoryCategory.WORK

    extracted_facts = fact_extractor.extract_from_text(clean_text)
    committed_nodes = []

    for f in extracted_facts:
        node = conflict_resolver.resolve_and_commit(
            subject=f["subject"],
            predicate=f["predicate"],
            object_=f["object"],
            category=f.get("category", cat_enum),
            scope=scope,
            confidence=f.get("confidence", 0.95),
            ymyl_protected=f.get("ymyl", False),
        )
        committed_nodes.append(node)

    if not committed_nodes:
        # Fallback commit directly
        node = conflict_resolver.resolve_and_commit(
            subject="user",
            predicate="noted",
            object_=clean_text,
            category=cat_enum,
            scope=scope,
            confidence=0.9,
        )
        committed_nodes.append(node)

    reports = [
        f"- [{n.category.value.upper()}] {n.to_readable_fact()} (Scope: {n.scope}, ID: {n.id[:8]})"
        for n in committed_nodes
    ]
    return f"Successfully remembered {len(committed_nodes)} fact(s):\n" + "\n".join(reports)


@mcp.tool()
def recall_memory(
    query: str,
    scope: str = "global",
    top_k: int = 5,
    category: Optional[str] = None,
) -> str:
    """Retrieve verified personal and project context matching a query, isolated by workspace scope."""
    cat_enum = None
    if category:
        try:
            cat_enum = MemoryCategory(category.lower())
        except ValueError:
            pass

    results = hybrid_retriever.retrieve(query, top_k=top_k, scope=scope, category=cat_enum)
    if not results:
        return f"No relevant memories found in scope '{scope}'."

    formatted = []
    for r in results:
        node = r.node
        formatted.append(
            f"- [{node.category.value.upper()}] {node.to_readable_fact()} "
            f"(Scope: {node.scope}, Confidence: {int(node.confidence * 100)}%, Source: {r.retrieval_source})"
        )
    return "\n".join(formatted)


@mcp.tool()
def verify_against_memory(
    proposal: str,
    scope: str = "global",
) -> str:
    """
    Active architectural guardrail and invariant policy checker.
    Audits an intended technical decision or code plan against known memory nodes.
    """
    return guardrail.check_proposal(proposal=proposal, scope=scope)


@mcp.tool()
def get_entity_subgraph(
    entity: str,
    max_hops: int = 1,
    scope: str = "global",
) -> str:
    """
    Explore relational knowledge graph connections centered around an entity.
    """
    nodes = graph_store.get_entity_subgraph(entity=entity, max_hops=max_hops, scope=scope)
    if not nodes:
        return f"No relational connections found for entity '{entity}' in scope '{scope}'."

    lines = [f"Knowledge Subgraph for '{entity}' (Scope: {scope}, Total nodes: {len(nodes)}):"]
    for n in nodes:
        lines.append(f"  ├── [{n.predicate}] ──► {n.object} (Subject: {n.subject}, Category: {n.category.value})")
    return "\n".join(lines)


@mcp.tool()
def commit_fact(
    subject: str,
    predicate: str,
    object_: str,
    category: str = "preference",
    scope: str = "global",
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
        scope=scope,
        confidence=1.0,
        ymyl_protected=ymyl_protected,
    )
    return f"Successfully committed memory node: {node.to_readable_fact()} (Scope: {node.scope}, ID: {node.id})"


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


# Dynamic MCP Resources for Zero-Turn Context Injection
if mcp is not None and hasattr(mcp, "resource"):

    @mcp.resource("memory://rules/{scope}")
    def get_scope_rules_resource(scope: str) -> str:
        """Auto-injected MCP resource providing architectural invariants and rules for the workspace."""
        active_nodes = graph_store.get_active_nodes(scope=scope)
        work_nodes = [n for n in active_nodes if n.category in (MemoryCategory.WORK, MemoryCategory.PREFERENCE)]
        if not work_nodes:
            return f"# Architectural Rules for {scope}\nNo specific rules recorded yet."

        lines = [f"# Architectural Rules for {scope}"]
        for n in work_nodes:
            lines.append(f"- [{n.category.value.upper()}] {n.to_readable_fact()}")
        return "\n".join(lines)

    @mcp.resource("memory://active-goals")
    def get_goals_resource() -> str:
        """Auto-injected MCP resource providing current user commitments and goals."""
        commitments = success_tracker.get_active_commitments()
        if not commitments:
            return "# Active Goals\nNo active commitments."

        lines = ["# Active Goals & Commitments"]
        for c in commitments:
            deadline = f" (Deadline: {c.target_deadline.strftime('%Y-%m-%d')})" if c.target_deadline else ""
            lines.append(f"- [{c.status.value.upper()}] {c.title}{deadline}")
        return "\n".join(lines)


# MCP Prompt Templates
if mcp is not None and hasattr(mcp, "prompt"):

    @mcp.prompt("agent-kickoff")
    def agent_kickoff_prompt(scope: str = "global") -> str:
        """Bootstrap an AI agent session with active goals and repository architectural rules."""
        rules_text = get_scope_rules_resource(scope)
        goals_text = get_goals_resource()
        return (
            "You are an autonomous AI coding agent connected to Baby LLM sovereign memory.\n"
            f"Active Workspace Scope: {scope}\n\n"
            f"{rules_text}\n\n"
            f"{goals_text}\n\n"
            "Guidelines: Adhere strictly to the architectural rules above. Before making breaking design changes, "
            "call `verify_against_memory(proposal)`. When learning new project conventions, call `remember(text)`."
        )


def run_mcp_server() -> None:
    """Run standard stdio MCP server for Cursor & Claude Desktop."""
    mcp.run()


if __name__ == "__main__":
    run_mcp_server()
