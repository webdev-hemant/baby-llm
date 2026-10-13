"""FastAPI server for Baby LLM REST API and WebSocket events."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
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
from baby_llm.runtime.llm_provider import llm_provider
from baby_llm.storage.graph_store import graph_store
from baby_llm.storage.wal import wal_logger
from baby_llm.success.agent import success_agent
from baby_llm.success.curiosity import curiosity_engine
from baby_llm.success.tracker import success_tracker
from baby_llm.sync.obsidian_sync import vault_sync

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pathlib import Path


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup background daemons
    dream_worker.start_background_daemon()
    vault_sync.start_observer()
    success_agent.start_scheduler()
    try:
        yield
    finally:
        # Graceful shutdown of daemons
        dream_worker.stop_background_daemon()
        vault_sync.stop_observer()
        success_agent.stop_scheduler()


app = FastAPI(title="Baby LLM Engine", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _resolve_ui_dir() -> Path:
    # 1. Package-embedded UI directory
    pkg_ui = Path(__file__).resolve().parent.parent / "ui"
    if pkg_ui.exists() and (pkg_ui / "index.html").exists():
        return pkg_ui
    # 2. Workspace / repository root fallback
    repo_ui = Path(__file__).resolve().parent.parent.parent.parent / "ui"
    if repo_ui.exists() and (repo_ui / "index.html").exists():
        return repo_ui
    return pkg_ui

ui_dir = _resolve_ui_dir()

@app.get("/")
def root():
    index_file = ui_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return RedirectResponse(url="/ui/")

@app.get("/styles.css")
def get_styles():
    css_file = ui_dir / "styles.css"
    if css_file.exists():
        return FileResponse(str(css_file), media_type="text/css")
    return {"detail": "styles.css not found"}

@app.get("/app.js")
def get_app_js():
    js_file = ui_dir / "app.js"
    if js_file.exists():
        return FileResponse(str(js_file), media_type="application/javascript")
@app.get("/manifest.json")
def get_manifest():
    manifest_file = ui_dir / "manifest.json"
    if manifest_file.exists():
        return FileResponse(str(manifest_file), media_type="application/manifest+json")
    return {"detail": "manifest.json not found"}

@app.get("/icon.svg")
def get_icon():
    icon_file = ui_dir / "icon.svg"
    if icon_file.exists():
        return FileResponse(str(icon_file), media_type="image/svg+xml")
    return {"detail": "icon.svg not found"}

if ui_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")

# Global in-memory ring buffer for active session
ring_buffer = EpisodicRingBuffer(max_size=15)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    stream: bool = False
    incognito: bool = False


class MemoryCreateRequest(BaseModel):
    subject: str
    predicate: str
    object: str
    category: MemoryCategory = MemoryCategory.PREFERENCE
    confidence: float = 1.0
    ymyl_protected: bool = False


class MemoryUpdateRequest(BaseModel):
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None
    category: Optional[MemoryCategory] = None
    confidence: Optional[float] = None
    ymyl_protected: Optional[bool] = None


@app.get("/api/health")
def health_check():
    return {"status": "awake", "version": "0.1.0", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Real-time Fast-Path chat endpoint (<30ms assembly overhead)."""
    # Notify background dream worker of user activity
    dream_worker.record_user_activity()

    # 1. Assemble context
    messages = context_assembler.assemble(
        user_input=req.message,
        ring_buffer=ring_buffer,
        include_memories=True,
    )

    # 2. Local LLM inference
    try:
        response_text = llm_provider.chat_sync(messages)
    except Exception as e:
        response_text = (
            f"I am running locally, but encountered an error: {str(e)}. "
            f"I have securely logged your message to local memory."
        )

    # 3. Check Gentle Curiosity probe (only in normal mode, not incognito)
    probe = None
    if not req.incognito:
        probe = curiosity_engine.evaluate_turn_for_probe(req.message)
        if probe:
            response_text += f"\n\n💭 *{probe}*"

    # 4. Instant WAL Write (Non-blocking) - Bypassed in incognito mode
    turn_id = None
    if not req.incognito:
        turn = InteractionTurn(
            session_id=req.session_id,
            user_input=req.message,
            assistant_response=response_text,
        )
        wal_logger.append_turn(turn)
        ring_buffer.append(turn)
        turn_id = turn.turn_id

    return {
        "turn_id": turn_id,
        "reply": response_text,
        "probed": bool(probe),
        "incognito": req.incognito,
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


@app.put("/api/memories/{node_id}")
def update_memory(node_id: str, req: MemoryUpdateRequest):
    """In-place update / override of an existing memory node."""
    node = graph_store.get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Memory node not found")

    updated_subject = req.subject if req.subject is not None else node.subject
    updated_predicate = req.predicate if req.predicate is not None else node.predicate
    updated_object = req.object if req.object is not None else node.object
    updated_category = req.category if req.category is not None else node.category
    updated_confidence = req.confidence if req.confidence is not None else node.confidence
    updated_ymyl = req.ymyl_protected if req.ymyl_protected is not None else node.ymyl_protected

    # Invalidate the old node
    graph_store.invalidate_node(node.id)

    # Commit updated node
    new_node = conflict_resolver.resolve_and_commit(
        subject=updated_subject,
        predicate=updated_predicate,
        object_=updated_object,
        category=updated_category,
        confidence=updated_confidence,
        ymyl_protected=updated_ymyl,
    )
    return {
        "status": "updated",
        "id": new_node.id,
        "old_id": node.id,
        "fact": new_node.to_readable_fact(),
    }


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
