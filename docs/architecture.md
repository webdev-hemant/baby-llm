# 🏛️ System Architecture & Runtime Topology

*System Topology, 4-Tier Memory Hierarchy, Runtime Lifecycles, Subsystem Interactions, and Concurrency*

---

## 1. Architectural Philosophy & Design Principles

Baby LLM is architected around four core design tenets that distinguish it from conventional AI agents and cloud-hosted memory services:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     FOUR CORE ARCHITECTURAL TENETS                     │
├────────────────────────┬───────────────────────────────────────────────┤
│ Tenet                  │ Architectural Guarantee                       │
├────────────────────────┼───────────────────────────────────────────────┤
│ 1. Offline Sovereignty │ Zero cloud calls; all data and weights local. │
│ 2. Real-Time Fast-Path │ Strict fast-path and background separation.   │
│ 3. Bi-Temporal Truth   │ Chronological history without data amnesia.   │
│ 4. Glass-Box Control   │ Inspect, edit, pin, or erase any memory node. │
└────────────────────────┴───────────────────────────────────────────────┘
```

### 1.1 The Fast-Path vs. Slow-Path Bifurcation
Most experimental memory frameworks commit a fatal architectural flaw: they execute multi-shot LLM extraction prompts synchronously on every user chat turn. This imposes a 3-to-8 second latency penalty per message, breaking natural conversational cadence.

Baby LLM strictly decouples real-time conversational inference from cognitive consolidation:
- **Synchronous Fast Path (<30ms)**: Memory retrieval (hybrid BM25 + dense vectors) and context compilation execute in milliseconds. The interaction turn is appended to a Write-Ahead Log (WAL) instantly without blocking the response.
- **Asynchronous Slow Path (REM Dream Worker)**: Atomic fact extraction, bi-temporal conflict resolution, and scientific Ebbinghaus decay execute in the background when the user is idle or during nightly consolidation windows.

---

## 2. System Topology & Subsystem Interactions

The Baby LLM architecture spans four distinct vertical layers:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   BABY LLM SYSTEM COMPONENT TOPOLOGY                   │
└────────────────────────────────────────────────────────────────────────┘

 [Interface Layer]
   ├─ Glass-Box Web Dashboard (Vanilla JS + Glassmorphic CSS, PWA)
   ├─ Interactive Terminal CLI (baby_llm.cli: chat, dream, memories)
   ├─ Universal MCP Server (FastMCP: stdio JSON-RPC protocol)
   └─ FastAPI REST Engine (Port 21225: /api/chat, /api/memories)
         │
         ▼
┌────────────────────────────────────────────────────────────────────────┐
│ RUNTIME & CONTEXT ASSEMBLY LAYER                                       │
│   ├─ ContextAssembler: Sub-20ms prompt compiler                        │
│   ├─ EpisodicRingBuffer: In-memory sliding window (last 15 turns)      │
│   ├─ GentleCuriosityEngine: Subtle clarifying question state machine   │
│   └─ UnifiedLLMProvider: Embedded Qwen2.5-0.5B (GGUF) + Ollama bridge  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STORAGE & BACKGROUND SUBSYSTEMS                                        │
│   ├─ SQLite WAL: interaction_log, memory_nodes, memory_fts (FTS5)      │
│   ├─ LanceDB: memories table (384-dim BGE vectors, cosine distance)    │
│   ├─ YMYL Security: AES-GCM-256 attribute encryption (OS Keyring)      │
│   ├─ REM Dream Worker: Background daemon for fact extraction & decay   │
│   ├─ Success Agent: 07:30 Morning Brief & 21:30 Reflection loops       │
│   └─ Obsidian Vault Sync: Watchdog observer for Markdown mirror        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The 4-Tier Biological Memory Hierarchy

Baby LLM models human cognitive architecture across four specialized memory tiers:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      THE 4-TIER MEMORY HIERARCHY                       │
├──────────┬──────────────────────┬────────────────────┬─────────────────┤
│ Tier     │ Subsystem            │ Persistence        │ Retention Scope │
├──────────┼──────────────────────┼────────────────────┼─────────────────┤
│ 1. RAM   │ EpisodicRingBuffer   │ collections.deque  │ 15 turns in RAM │
│ 2. WAL   │ WriteAheadLog        │ SQLite Table (WAL) │ Until dream     │
│ 3. Graph │ BiTemporalGraphStore │ SQLite + LanceDB   │ Ebbinghaus/YMYL │
│ 4. Vault │ VaultSyncManager     │ Markdown Files     │ Lifelong Memory │
└──────────┴──────────────────────┴────────────────────┴─────────────────┘
```

### Tier 1: Working Episodic Memory (`EpisodicRingBuffer`)
- **Implementation**: `src/baby_llm/core/ring_buffer.py`
- **Structure**: A fixed-size `collections.deque[InteractionTurn]` bounded to `max_size=15`.
- **Purpose**: Provides immediate, zero-latency short-term conversational context across recent dialogue turns without hitting disk.

### Tier 2: Short-Term Write-Ahead Log (`WriteAheadLog`)
- **Implementation**: `src/baby_llm/storage/wal.py`
- **Structure**: SQLite table `interaction_log` operating in WAL journal mode (`PRAGMA journal_mode = WAL;`).
- **Purpose**: Persists raw conversational turns (`turn_id`, `session_id`, `timestamp`, `user_input`, `assistant_response`, `processed_in_dream`). Writes take <1ms and guarantee that unhandled dialogue is never lost even if the process restarts.

### Tier 3: Long-Term Bi-Temporal Semantic Memory
- **Implementation**: `src/baby_llm/storage/graph_store.py` and `src/baby_llm/storage/vector_store.py`
- **Structure**: Normalized SQLite table `memory_nodes` combined with LanceDB dense vector index `memories`.
- **Key Fields**: Subject, Predicate, Object, Category, Confidence, Stability, `valid_from`, and `invalid_from`.
- **Bi-Temporal Property**: When the user updates a fact (*"I lived in London"* $\to$ *"I moved to Tokyo"*), London's `invalid_from` timestamp is closed, Tokyo is committed with `valid_from = now`, and both records remain queryable for historical trajectory reconstruction.

### Tier 4: Procedural Directives & Vault Markdown Sync
- **Implementation**: `src/baby_llm/runtime/context_assembler.py` and `src/baby_llm/sync/obsidian_sync.py`
- **Structure**: System-level persona definitions (`BASE_PERSONA_PROMPT`), daily morning briefs (`daily_summaries`), and bidirectional Markdown files in `~/.baby_llm/vault/memories/<node_id>.md`.
- **Purpose**: Bridges structured database records into human-readable plain text files compatible with Obsidian, Logseq, or Git.

---

## 4. Runtime Execution Lifecycles

### 4.1 Real-Time Chat Pipeline (Synchronous Fast Path)

```text
 [User Message]
       │
       ▼
 1. Record User Activity ──► Immediately pauses any active Dream Worker
       │
       ▼
 2. Hybrid Retrieval (<15ms)
       ├─ SQLite FTS5 BM25 Search (top 10)
       ├─ FastEmbed ONNX Dense Vector Search (top 10 cosine)
       └─ Reciprocal Rank Fusion (RRF: k=60) ──► Top 5 Active Memories
       │
       ▼
 3. Context Assembly (<2ms)
       ├─ System Persona Prompt (BASE_PERSONA_PROMPT)
       ├─ Injected Memories (Formatted Subject-Predicate-Object lines)
       ├─ Injected Commitments (Active open goals with deadlines)
       ├─ Episodic History (Deque turns from EpisodicRingBuffer)
       └─ Current User Message
       │
       ▼
 4. Unified Inference
       ├─ Attempt Embedded Qwen2.5-0.5B-Instruct-GGUF (llama-cpp-python)
       └─ Fallback to Local Ollama HTTP Daemon (http://localhost:11434)
       │
       ▼
 5. Gentle Curiosity Probe Check
       └─ Evaluates user message for ambiguous entities (max 1 probe/session)
       │
       ▼
 6. Instant Asynchronous Append
       ├─ Append Turn to SQLite WAL (interaction_log) [Non-blocking]
       └─ Append Turn to Episodic Ring Buffer
       │
       ▼
 [Streaming or Single Turn Response Delivered to User]
```

### 4.2 Asynchronous REM Dream Consolidation Pipeline

```text
 [Trigger: OS Idle Timeout (>=15m) OR Daily Nightly Cron (03:00 AM)]
       │
       ▼
 1. Check User Activity State
       └─ If user is actively typing, yield and postpone cycle
       │
       ▼
 2. Ingest Unprocessed WAL Turns
       └─ Fetch batch of turns where processed_in_dream = 0 (limit 50)
       │
       ▼
 3. Atomic Fact Extraction (FactExtractor)
       ├─ Local SLM parses turns into strict JSON array of SPO triples
       └─ Heuristic Regex fallback if SLM returns malformed data
       │
       ▼
 4. Bi-Temporal Contradiction Resolution (ConflictResolver)
       ├─ Search existing active nodes matching (subject, predicate)
       ├─ If identical object: Reinforce stability (S = S * 2.0)
       ├─ If conflicting object:
       │    ├─ Invalidate old node: invalid_from = now
       │    ├─ Update old node status in LanceDB: is_active = False
       │    └─ Commit new node with valid_from = now
       └─ Generate 384-dim vector & upsert to LanceDB memories table
       │
       ▼
 5. Mark WAL Turns as Processed
       └─ UPDATE interaction_log SET processed_in_dream = 1 WHERE turn_id IN (...)
       │
       ▼
 6. Scientific Ebbinghaus Decay Pruning (EbbinghausDecayEngine)
       ├─ Calculate retention R(t) = exp(-t / (S * I)) for all active nodes
       ├─ YMYL Shield: Health and finance facts locked to R(t) = 1.0
       └─ If R(t) < 0.20:
            ├─ Invalidate node in graph (invalid_from = now)
            └─ Deactivate in LanceDB vector index (is_active = False)
       │
       ▼
 [Consolidation Cycle Complete: Logs turn counts and archived node metrics]
```

---

## 5. Concurrency, Threading, and Synchronization

Baby LLM maintains thread safety across multi-threaded asynchronous daemons without distributed message brokers or heavy lock managers:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        THREAD CONCURRENCY MODEL                        │
├───────────────────────┬──────────────────────┬─────────────────────────┤
│ Thread Identifier     │ Managing Subsystem   │ Lifecycle & Role        │
├───────────────────────┼──────────────────────┼─────────────────────────┤
│ Main / Uvicorn Thread │ FastAPI App Server   │ Handles HTTP / REST     │
│ REMDreamDaemon        │ DreamWorker          │ Monitors idle & 03:00   │
│ SuccessAgentScheduler │ PersonalSuccessAgent │ Triggers 07:30 & 21:30  │
│ Watchdog Observer     │ VaultSyncManager     │ Monitors vault folder   │
└───────────────────────┴──────────────────────┴─────────────────────────┘
```

### Concurrency Primitives:
1. **Llama-CPP Thread Lock (`threading.Lock`)**: The embedded `Llama` C++ engine in `EmbeddedLLMEngine` is protected by a thread lock (`self._lock`) to ensure single-threaded execution during synchronous chat and extraction calls.
2. **User Activity Debounce (`threading.Event`)**: When a chat request arrives, `dream_worker.record_user_activity()` sets `self._pause_event`. Any running background consolidation yields immediately to prioritize interactive user compute. A 2.0-second timer then clears the pause flag.
3. **SQLite WAL Concurrency**: SQLite's Write-Ahead Logging mode (`PRAGMA journal_mode = WAL;`) allows multiple readers (FastAPI retrieval queries, CLI memory inspection) to execute concurrently while a writer appends to the log. The database connection timeout is configured to 30.0 seconds to eliminate `database locked` exceptions.

---

## 6. Failure Modes & Resiliency Strategies

| Subsystem Failure | Failure Detection | Automated Recovery / Fallback Behavior |
| :--- | :--- | :--- |
| **Local LLM Daemon Down** | HTTP connection error to `localhost:11434` | Automatically falls back to embedded `Qwen2.5-0.5B-Instruct-GGUF`. If both fail, safely records turn to WAL and returns offline acknowledgment. |
| **Malformed Extraction JSON** | `json.JSONDecodeError` in `FactExtractor` | Activates regex-based heuristic extractor for common assertions (`lives_in`, `works_as`, `allergic_to`). |
| **OS Keyring Unavailable** | `keyring.errors.KeyringError` | Automatically provisions fallback air-gapped 256-bit AES master key in `~/.baby_llm/.ymyl_key` with mode `0600`. |
| **Process Crash Mid-Turn** | Sudden OS shutdown / SIGKILL | SQLite WAL table preserves all un-consolidated turns. On next startup, `DreamWorker` picks up all pending records. |

---

## Next Steps
- Deep dive into the fast-path assembler, decay curves, and SLM extractor: **[core-engine.md](core-engine.md)**
- Review SQLite schemas, LanceDB tables, and encryption mechanics: **[configuration-and-storage.md](configuration-and-storage.md)**
- Explore CLI commands, REST APIs, and MCP tools: **[interfaces-and-api.md](interfaces-and-api.md)**
