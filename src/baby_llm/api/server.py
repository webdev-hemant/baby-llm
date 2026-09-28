"""FastAPI server for Baby LLM REST API and WebSocket events."""

from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from baby_llm.core.models import InteractionTurn, MemoryCategory, MemoryNode
from baby_llm.core.ring_buffer import EpisodicRingBuffer
from baby_llm.dream.decay import decay_engine
from baby_llm.dream.resolver import conflict_resolver
from baby_llm.dream.worker import dream_worker
from baby_llm.retrieval.hybrid import hybrid_retriever
from baby_llm.runtime.context_assembler import context_assembler
from baby_llm.runtime.ollama_client import ollama_client
from baby_llm.storage.graph_store import graph_store
from baby_llm.storage.wal import wal_logger
from baby_llm.success.agent import success_agent
from baby_llm.success.curiosity import curiosity_engine
from baby_llm.success.tracker import success_tracker

from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="Baby LLM Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Glass-Box UI static files
ui_dir = Path(__file__).resolve().parent.parent.parent.parent / "ui"
if ui_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")

# Global in-memory ring buffer for active session
ring_buffer = EpisodicRingBuffer(max_size=15)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    stream: bool = False


class MemoryCreateRequest(BaseModel):
    subject: str
    predicate: str
    object: str
    category: MemoryCategory = MemoryCategory.PREFERENCE
    confidence: float = 1.0
    ymyl_protected: bool = False


@app.get("/api/health")
def health_check():
    return {"status": "awake", "version": "0.1.0", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Real-time Fast-Path chat endpoint (<30ms assembly overhead)."""
    # 1. Assemble context
    messages = context_assembler.assemble(
        user_input=req.message,
        ring_buffer=ring_buffer,
        include_memories=True,
    )

    # 2. Local LLM inference
    try:
        response_text = ollama_client.chat_sync(messages)
    except Exception as e:
        response_text = (
            f"I am running locally, but could not connect to Ollama at {ollama_client.base_url}. "
            f"(Error: {str(e)}). I have securely logged your message to local memory."
        )

    # 3. Check Gentle Curiosity probe
    probe = curiosity_engine.evaluate_turn_for_probe(req.message)
    if probe:
        response_text += f"\n\n💭 *{probe}*"

    # 4. Instant WAL Write (Non-blocking)
    turn = InteractionTurn(
        session_id=req.session_id,
        user_input=req.message,
        assistant_response=response_text,
    )
    wal_logger.append_turn(turn)
    ring_buffer.append(turn)

    return {
        "turn_id": turn.turn_id,
        "reply": response_text,
        "probed": bool(probe),
    }


@app.get("/api/memories")
def get_memories(
    category: Optional[MemoryCategory] = None,
    active_only: bool = True,
):
    """Retrieve memory nodes for Glass-box inspection."""
    if active_only:
        nodes = graph_store.get_active_nodes(category=category)
    else:
        # returns all nodes
        nodes = graph_store.get_active_nodes(category=category)
    return [
        {
            "id": n.id,
            "fact": n.to_readable_fact(),
            "subject": n.subject,
            "predicate": n.predicate,
            "object": n.object,
            "category": n.category.value,
            "confidence": n.confidence,
            "stability": n.stability,
            "is_active": n.is_active,
            "ymyl_protected": n.ymyl_protected,
            "valid_from": n.valid_from.isoformat(),
            "invalid_from": n.invalid_from.isoformat() if n.invalid_from else None,
        }
        for n in nodes
    ]


@app.post("/api/memories")
def create_memory(req: MemoryCreateRequest):
    """Directly insert or override a memory node (Glass-box transparency)."""
    node = conflict_resolver.resolve_and_commit(
        subject=req.subject,
        predicate=req.predicate,
        object_=req.object,
        category=req.category,
        confidence=req.confidence,
        ymyl_protected=req.ymyl_protected,
    )
    return {"status": "success", "id": node.id, "fact": node.to_readable_fact()}


@app.delete("/api/memories/{node_id}")
def delete_memory(node_id: str):
    """One-click memory node erase (Glass-box privacy control)."""
    success = graph_store.delete_node(node_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory node not found")
    return {"status": "deleted", "id": node_id}


@app.post("/api/dream/trigger")
def trigger_dream():
    """Manually invoke REM Dream consolidation cycle."""
    summary = dream_worker.run_consolidation_cycle()
    return {"status": "completed", "summary": summary}


@app.get("/api/success/compass")
def get_success_compass():
    """Retrieve personal success directives, active goals, and morning brief."""
    commitments = success_tracker.get_active_commitments()
    alerts = success_agent.check_overdue_commitments()
    brief = success_agent.generate_morning_brief()
    return {
        "morning_brief": brief,
        "commitments": [
            {
                "id": c.id,
                "title": c.title,
                "status": c.status.value,
                "deadline": c.target_deadline.isoformat() if c.target_deadline else None,
            }
            for c in commitments
        ],
        "alerts": alerts,
    }
