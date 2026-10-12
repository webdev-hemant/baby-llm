# Baby LLM: Comprehensive Implementation Plan
*A Privacy-First, Self-Evolving Local Memory & Life Success Engine*

---

## 1. Executive Overview & System Topology

**Baby LLM** is an autonomous, local-first cognitive companion designed to bridge the gap between stateless local LLMs and long-term personal context. Rather than treating memory as an afterthought or relying on cloud APIs, Baby LLM runs completely offline on consumer hardware with zero latency overhead on the real-time chat path.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BABY LLM RUNTIME TOPOLOGY                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ USER INTERFACES & INTEGRATION HOOKS                                         │
│ • Glass-Box Web Dashboard & PWA (Port 21225)                                │
│ • Claude Desktop / Cursor / Zed (Universal MCP)                             │
│ • Terminal CLI & Raycast Quick Entry                                        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                      User Prompt /    │ Streaming Response
                      Context Query    │ (< 30ms fast-path overhead)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. DAYTIME FAST-PATH ENGINE (Synchronous, Zero-Lag)                         │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Working Context Assembler                                           │   │
│   │  • Episodic Ring Buffer: Last 10-15 conversational turns            │   │
│   │  • Hybrid Sub-20ms Retrieval:                                       │   │
│   │      - BM25 Full-Text Search (SQLite FTS5) for exact entities       │   │
│   │      - Dense Vector Search (LanceDB + BGE-Small-EN-v1.5)            │   │
│   │  • Static Identity & Active Directives Injection                    │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│                  Local Inference Engine (Embedded llama-cpp-python / Ollama) │
│                  Default Model: Qwen2.5-0.5B-Instruct-GGUF (~398MB, <450MB) │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                      Instant Append   │ (Zero-blocking write)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. WRITE-AHEAD INTERACTION LOG (WAL - SQLite Embedded)                      │
│    • Unprocessed turns • Timestamps • Sentiment • Task markers              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                      Triggered on     │ Idle (> 15m) or Night Timer (03:00)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. THE "REM DREAM" CONSOLIDATION ENGINE (Asynchronous Background Worker)    │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Quantized SLM Worker (Embedded Qwen2.5-0.5B-Instruct GGUF)          │   │
│   │  • Step A: SPO Fact Extraction (Subject, Predicate, Object Triples) │   │
│   │  • Step B: Bi-Temporal Conflict Resolution (valid_from / to)        │   │
│   │  • Step C: Ebbinghaus Retention Decay & Reinforcement Computation   │   │
│   │  • Step D: YMYL Immunity Shield & Cold-Vault Archival               │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│          Bi-Temporal Relational Graph (SQLite) & Vector Store (LanceDB)      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. PERSONAL SUCCESS & GLASS-BOX INTEGRATION                                 │
│    • Morning Intention (07:30) & Evening Reflection (21:30) Loops           │
│    • Universal MCP Server (recall_memory, commit_fact, get_active_goals)    │
│    • Bidirectional Obsidian / Local Markdown Vault Synchronization          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Target Directory & Module Structure

The project follows a clean, modular 100% Python architecture with an embedded Glass-Box web dashboard served directly via FastAPI.

```text
personal_success-manager/
├── docs/
│   └── baby-llm-reasearch/
│       ├── baby_llm_product_blueprint.md
│       └── local_llm_memory_research.md
├── implementation/
│   └── baby-llm/
│       └── IMPLEMENTATION_PLAN.md
├── src/
│   └── baby_llm/
│       ├── __init__.py
│       ├── config.py                 # Core app configuration & environment paths
│       ├── core/
│       │   ├── __init__.py
│       │   ├── models.py             # Pydantic data schemas (Node, Turn, Goal)
│       │   └── ring_buffer.py        # In-memory episodic buffer
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── db.py                 # SQLite connection manager & migrations
│       │   ├── wal.py                # Write-Ahead interaction log operations
│       │   ├── graph_store.py        # Bi-temporal SPO graph CRUD
│       │   └── vector_store.py       # LanceDB vector table & indexing
│       ├── retrieval/
│       │   ├── __init__.py
│       │   ├── embedder.py           # Local fast embedding (BGE-Small-EN-v1.5 ONNX)
│       │   ├── bm25.py               # SQLite FTS5 exact search
│       │   └── hybrid.py             # Reciprocal Rank Fusion (RRF) retriever
│       ├── runtime/
│       │   ├── __init__.py
│       │   ├── embedded_engine.py    # Embedded llama-cpp-python GGUF engine
│       │   ├── llm_provider.py       # Unified LLM provider (Embedded / Ollama)
│       │   ├── ollama_client.py      # Optional external Ollama streaming connector
│       │   └── context_assembler.py  # Sub-20ms prompt compiler
│       ├── dream/
│       │   ├── __init__.py
│       │   ├── worker.py             # Asynchronous idle / scheduled loop
│       │   ├── extractor.py          # Sub-2B SLM atomic fact parser
│       │   ├── resolver.py           # Temporal conflict & contradiction resolver
│       │   └── decay.py              # Ebbinghaus retention & YMYL evaluator
│       ├── success/
│       │   ├── __init__.py
│       │   ├── agent.py              # Proactive loop (Morning, Watchdog, Evening)
│       │   ├── tracker.py            # Commitments & goals state-machine
│       │   └── curiosity.py          # Gentle curiosity questioning engine
│       ├── mcp/
│       │   ├── __init__.py
│       │   └── server.py             # Universal Model Context Protocol server (stdio/SSE)
│       ├── sync/
│       │   ├── __init__.py
│       │   └── obsidian_sync.py      # Watchdog-based bidirectional Markdown sync
│       └── api/
│           ├── __init__.py
│           └── server.py             # FastAPI local REST & WebSocket service
├── ui/                               # Glass-Box Web Dashboard & PWA
│   ├── index.html                    # Glass-Box single-page interface
│   ├── styles.css                    # Fluid, zero-scroll responsive theme
│   ├── app.js                        # Dynamic REST/SSE reactive state engine
│   └── manifest.json                 # PWA standalone desktop installation
├── tests/
│   ├── unit/
│   │   ├── test_wal.py
│   │   ├── test_graph_store.py
│   │   ├── test_decay.py
│   │   └── test_hybrid_retrieval.py
│   └── integration/
│       ├── test_dream_cycle.py
│       └── test_mcp_server.py
├── pyproject.toml
└── README.md
```

---

## 3. Storage Schema & Mathematical Formulations

### 3.1 SQLite Relational & Bi-Temporal Schema

```sql
-- 1. Write-Ahead Interaction Log
CREATE TABLE IF NOT EXISTS interaction_log (
    turn_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_input TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    sentiment_tag TEXT,
    processed_in_dream BOOLEAN DEFAULT 0
);

-- 2. Core Bi-Temporal Memory Nodes
CREATE TABLE IF NOT EXISTS memory_nodes (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    category TEXT CHECK(category IN ('lifestyle', 'health', 'finance', 'work', 'relationship', 'goal', 'preference')),
    confidence REAL DEFAULT 1.0,
    stability REAL DEFAULT 1.0,               -- Ebbinghaus stability factor (doubles on recall)
    last_reinforced_at TIMESTAMP NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    invalid_from TIMESTAMP,                   -- NULL denotes currently active
    ymyl_protected BOOLEAN DEFAULT 0,         -- 1 = Immune from temporal decay
    source_turn_id TEXT REFERENCES interaction_log(turn_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Full-Text Search Virtual Table (FTS5)
CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    id UNINDEXED,
    subject,
    predicate,
    object,
    category,
    content='memory_nodes',
    content_rowid='rowid'
);

-- 4. Commitments & Success Tracking
CREATE TABLE IF NOT EXISTS commitments (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'dropped')) DEFAULT 'pending',
    target_deadline TIMESTAMP,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    associated_node_id TEXT REFERENCES memory_nodes(id)
);
```

### 3.2 Scientific Ebbinghaus Forgetting & Decay Model

The retention probability $R(t)$ of a memory node at time $t$ (in days) since its last reinforcement is given by:

$$R(t) = \exp\left( -\frac{t}{S \cdot I} \right)$$

Where:
* $t$: Elapsed days since `last_reinforced_at`.
* $S$: Memory Stability (starts at $1.0$, increases as $S_{new} = S_{old} \times 2.0$ whenever referenced or validated).
* $I$: Importance Weight ($1.0$ to $3.0$).
* **YMYL Immunity**: If `ymyl_protected == 1`, $R(t) \equiv 1.0$ (never pruned).
* **Pruning / Archival Policy**:
  * If $R(t) \ge 0.50$: Node is **Active** in Fast-Path context & LanceDB.
  * If $0.20 \le R(t) < 0.50$: Node is **Dormant** (only retrieved on high-threshold exact query).
  * If $R(t) < 0.20$: Node is **Archived** to cold storage JSONL.

---

## 4. Phase-by-Phase Execution Roadmap

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXECUTION PHASING (12 WEEKS)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 1: Fast-Path Engine & WAL Store                       (Weeks 1 - 3)   │
│ • SQLite WAL logger & In-Memory Ring Buffer                                 │
│ • LanceDB Vector Store + ONNX BGE Embeddings                                │
│ • FTS5 BM25 + Vector Hybrid Retrieval (RRF)                                 │
│ • Zero-lag Context Assembler + Embedded Qwen2.5-0.5B Engine                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 2: The REM Dream Engine & Bi-Temporal Graph           (Weeks 4 - 6)   │
│ • Asynchronous background worker (Idle detection & Cron)                    │
│ • Quantized sub-1B SLM (Qwen2.5-0.5B) Atomic SPO Triple extraction          │
│ • Bi-temporal resolution (valid_from / invalid_from)                        │
│ • Ebbinghaus decay calculator with YMYL Shield                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 3: Universal MCP Server & Glass-Box Dashboard         (Weeks 7 - 9)   │
│ • Model Context Protocol (MCP) Server (stdio/SSE)                           │
│ • Glass-Box Web UI & PWA (Mindstream, Timeline & Compass)                   │
│ • Direct user editing: Pin, Edit, Erase, Incognito Mode                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 4: Proactive Success Agent & Local Ecosystem Sync    (Weeks 10 - 12)  │
│ • Morning Brief (07:30), Nightly Reflection (21:30), Curiosity Protocol     │
│ • Bidirectional Obsidian / Local Markdown Vault sync                        │
│ • End-to-end benchmarking, privacy auditing, and packaging                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Fast-Path Engine & WAL Store (Weeks 1 – 3)

#### Goal
Establish a zero-lag (< 30ms overhead) chat pipeline that retrieves relevant context and instantly appends conversation logs without blocking the user.

#### Key Tasks
1. **Repository & Environment Scaffolding**
   * Setup `pyproject.toml` with `fastapi`, `uvicorn`, `lancedb`, `pydantic`, `onnxruntime`, `httpx`, `watchdog`, `mcp`.
   * Configure project pathing (`~/.baby_llm/` for databases, vector tables, and logs).
2. **SQLite Infrastructure & WAL Logger**
   * Implement `src/baby_llm/storage/db.py` ensuring `PRAGMA journal_mode = WAL`, `PRAGMA synchronous = NORMAL`, and foreign keys enabled.
   * Build `src/baby_llm/storage/wal.py` to write raw user/assistant turns in sub-millisecond threads.
3. **Local Embedding Engine**
   * Implement `src/baby_llm/retrieval/embedder.py` utilizing `bge-small-en-v1.5` in ONNX runtime for ultra-fast, local CPU/GPU embedding generation (384 dimensions).
4. **Hybrid Retrieval Pipeline (FTS5 BM25 + LanceDB)**
   * Implement `src/baby_llm/storage/vector_store.py` connecting to LanceDB.
   * Implement `src/baby_llm/retrieval/bm25.py` for keyword matches on `memory_fts`.
   * Implement `src/baby_llm/retrieval/hybrid.py` using Reciprocal Rank Fusion (RRF):
     $$RRF\_Score(d) = \sum_{m \in \{bm25, vector\}} \frac{1}{60 + rank_m(d)}$$
5. **Context Assembler & Embedded Qwen2.5 Inference Engine**
   * Build `src/baby_llm/runtime/context_assembler.py` to merge:
     * System Persona & Developmental Stage Directive.
     * Top-K Retrieved Memories (Bi-temporal valid only).
     * Recent Ring Buffer (last 10 turns).
   * Stream completion via `src/baby_llm/runtime/llm_provider.py` backed by `embedded_engine.py` (`Qwen2.5-0.5B-Instruct-GGUF` ~398MB) with optional external Ollama fallback.

#### Deliverables & Acceptance Criteria
* CLI chat interface running 100% self-contained locally via embedded Qwen2.5-0.5B (zero external Ollama daemon required).
* Benchmarked latency: Context assembly completes in under 25ms.
* Zero lost turns in `interaction_log`.

---

### Phase 2: The REM Dream Engine & Bi-Temporal Graph (Weeks 4 – 6)

#### Goal
Implement the autonomous background consolidation process that extracts facts, resolves temporal contradictions, and manages memory decay without interfering with daytime performance.

#### Key Tasks
1. **Idle & Scheduling Daemon**
   * Build `src/baby_llm/dream/worker.py` utilizing OS idle timers (e.g., Mac IOKit or cross-platform activity checks) and cron fallback (03:00 AM).
   * Ensure concurrency guards: Pause dream worker immediately if the user interacts with the app.
2. **Atomic Triple Extraction Pipeline**
   * Implement `src/baby_llm/dream/extractor.py` utilizing the quantized sub-1B embedded SLM (`Qwen2.5-0.5B-Instruct-GGUF` via `embedded_engine.py` or optional Ollama).
   * Output strict JSON schema: `[{"subject": "...", "predicate": "...", "object": "...", "category": "...", "confidence": 0.95, "ymyl": false}]`.
3. **Bi-Temporal Conflict Resolution Engine**
   * Implement `src/baby_llm/dream/resolver.py`:
     * When a new triple contradicts an existing active node:
       * Set existing node's `invalid_from = CURRENT_TIMESTAMP`.
       * Insert new node with `valid_from = CURRENT_TIMESTAMP`, `invalid_from = NULL`.
     * Preserves entire historical trajectory for timeline inspection.
4. **Ebbinghaus Decay & YMYL Shield**
   * Implement `src/baby_llm/dream/decay.py`:
     * Compute $R(t)$ for all active nodes.
     * Enforce YMYL category immunity (finance, health, core values).
     * Mark nodes with $R(t) < 0.20$ as archived; remove from active LanceDB vector index to maintain optimal retrieval speeds.

#### Deliverables & Acceptance Criteria
* Automated test running dream consolidation over a synthetic 30-day dialogue history.
* Accurate contradiction handling (e.g., verifying that "lives in Seattle" closes when "moved to Austin" is learned).
* Memory retention math verified via unit tests.

---

### Phase 3: Universal MCP Server & Glass-Box Dashboard (Weeks 7 – 9)

#### Goal
Provide an open ecosystem interface for external tools (Cursor, Claude Desktop) and a native "glass-box" desktop dashboard for complete transparency and user control.

#### Key Tasks
1. **Universal Model Context Protocol (MCP) Server**
   * Implement `src/baby_llm/mcp/server.py` using official MCP Python SDK.
   * Expose standard tools:
     * `recall_memory(query: str, category: Optional[str]) -> List[MemoryNode]`
     * `commit_fact(subject: str, predicate: str, object: str, ymyl: bool) -> str`
     * `get_active_goals() -> List[Commitment]`
     * `record_daily_win(note: str) -> str`
   * Support stdio transport for Cursor / Claude Desktop configuration.
2. **FastAPI Desktop Bridge (Port 21225)**
   * Implement `src/baby_llm/api/server.py` exposing REST endpoints on dedicated collision-proof port `21225` (spelling "BABY"):
     * `GET /api/memories?status=active`
     * `POST /api/memories/override`
     * `DELETE /api/memories/{id}`
     * `GET /api/success/compass`
3. **Glass-Box Web Dashboard & PWA**
   * Built-in browser/PWA UI served directly by FastAPI at port 21225 (Vanilla CSS/HTML/JS for instant load and < 30MB RAM footprint).
   * Accessible via `baby-llm ui` CLI launcher or direct browser navigation to `http://127.0.0.1:21225`.
   * **Mindstream Panel**: Visual interactive cards showing newly consolidated facts with confidence tags.
   * **Bi-Temporal Timeline View**: Visual timeline showing past vs. present states.
   * **One-Click Erase & Edit**: Immediate user correction of any memory node.
   * **Incognito Mode**: Temporary toggle disabling WAL logging for sensitive chats.
   * **PWA Standalone Mode**: Web app manifest (`manifest.json`) enabling one-click installation to macOS Dock or Windows Taskbar as an isolated window.

#### Deliverables & Acceptance Criteria
* Working integration with Claude Desktop and Cursor IDE via `baby-llm-mcp`.
* Functional Glass-Box web dashboard displaying memory nodes, success metrics, and offering full CRUD on memory nodes.

---

### Phase 4: Proactive Success Agent & Local Vault Sync (Weeks 10 – 12)

#### Goal
Transform Baby LLM from a passive memory store into an active personal success partner with bidirectional Obsidian synchronization.

#### Key Tasks
1. **Personal Success Loops**
   * Implement `src/baby_llm/success/agent.py`:
     * **Morning Intention Brief (07:30 AM)**: Formulates top 2 needle-moving priorities and unresolved loops.
     * **Nightly Reflection & Unload (09:30 PM)**: Frictionless daily win capture and mental unloading.
     * **Accountability Watchdog**: Checks overdue commitments and gently surfaces them.
2. **Gentle Curiosity Protocol**
   * Implement `src/baby_llm/success/curiosity.py`:
     * Tracks entity ambiguity in dialogues.
     * Restricts proactive probing to at most **one** gentle question per session to maintain trust without annoying the user.
3. **Obsidian / Local Markdown Vault Synchronization**
   * Implement `src/baby_llm/sync/obsidian_sync.py` using `watchdog`:
     * Exports memory nodes to `~/BabyLLM/vault/memories/*.md` with YAML front-matter.
     * Reads user edits in Obsidian markdown files and propagates changes back to SQLite and LanceDB automatically.
4. **Hardening, Security & Packaging**
   * Encrypt sensitive YMYL attributes using AES-GCM-256 with keys stored in the OS Keyring.
   * Standard Python packaging via `pyproject.toml` (`pip install baby-llm` or `pip install -e .`).
   * Streamlined CLI commands: `baby-llm chat`, `baby-llm serve`, `baby-llm ui`, `baby-llm dream`.

#### Deliverables & Acceptance Criteria
* Proactive briefing messages triggered on time.
* Real-time bidirectional file sync between Markdown files and SQLite/LanceDB verified.
* Zero cloud dependencies verified via network traffic monitoring.

---

## 5. Technology Matrix & Resource Budgets

| Component | Technology | Footprint / Latency Budget |
| :--- | :--- | :--- |
| **Glass-Box Dashboard** | Built-in Web UI & PWA (Port 21225) | RAM: < 30MB |
| **Backend Core** | Python 3.12+ / FastAPI (Port 21225) | Idle RAM: ~60MB |
| **Relational Storage** | SQLite (WAL mode) | Read/Write: < 2ms |
| **Vector DB** | LanceDB (columnar, disk-native) | Search: < 10ms for 100k vectors |
| **Local Embedder** | ONNX `bge-small-en-v1.5` | Latency: ~8ms on CPU (384-dim) |
| **Default Embedded SLM** | **`Qwen2.5-0.5B-Instruct-GGUF`** (`llama-cpp-python`) | **Disk: ~398MB, RAM: < 450MB (Self-contained)** |
| **Optional External LLM** | Ollama (`llama3.2:3b` / `qwen2.5:7b`) | VRAM: 2.0GB – 4.5GB (Optional) |
| **Dream Consolidation SLM** | `Qwen2.5-0.5B-Instruct` (Embedded / Unified) | Runs in background with thread-safe lock |
| **Security Layer** | AES-GCM-256 via OS Keyring | Negligible overhead |

---

## 6. Verification, Testing & Milestones Checklist

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VERIFICATION GATES                                 │
├────┬─────────────────────────────┬──────────────────────────────────────────┤
│ #  │ Verification Gate           │ Validation Metric                        │
├────┼─────────────────────────────┼──────────────────────────────────────────┤
│ G1 │ Fast-Path Latency Overhead  │ Context retrieval + assembly < 30ms      │
│ G2 │ Contradiction Accuracy      │ > 95% on synthetic conflict test suite   │
│ G3 │ Memory Decay Mathematics    │ Retention curves conform to Ebbinghaus   │
│ G4 │ YMYL Immunity               │ 100% retention on protected categories   │
│ G5 │ Background Resource Ceiling │ Dream worker consumes < 1.0GB RAM/VRAM   │
│ G6 │ MCP Client Compatibility    │ Works seamlessly in Cursor and Claude    │
│ G7 │ Air-Gapped Privacy          │ 0 outbound cloud requests during tests   │
└────┴─────────────────────────────┴──────────────────────────────────────────┘
```

---

## 7. Next Actions

To begin execution of **Phase 1**:
1. Initialize the Python virtual environment and `pyproject.toml` dependencies.
2. Implement the SQLite schema (`interaction_log`, `memory_nodes`, `commitments`) and WAL logger.
3. Configure LanceDB with the local ONNX embedding pipeline.
