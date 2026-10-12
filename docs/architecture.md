# 🏛️ System Architecture & Runtime Topology

*Tripartite Interaction Model, Sub-30ms Agent Substrate, 4-Tier Memory Hierarchy, Runtime Lifecycles, and Concurrency*

---

## 1. Architectural Philosophy & Design Principles

Baby LLM is engineered as a **sovereign long-term memory engine and cognitive substrate**. Unlike monolithic chatbots or third-party cloud memory SaaS, it decouples fast-path memory retrieval for autonomous agents from asynchronous subconscious consolidation:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     FOUR CORE ARCHITECTURAL TENETS                     │
├────────────────────────┬───────────────────────────────────────────────┤
│ Tenet                  │ Architectural Guarantee                       │
├────────────────────────┼───────────────────────────────────────────────┤
│ 1. Sovereign Agent Hub │ 100% offline memory substrate for AI agents.  │
│ 2. Sub-30ms Fast Path  │ Zero latency stalls for external tool calls.  │
│ 3. Model-to-Model REM  │ Subconscious SLM extracts & prunes memories.  │
│ 4. Bi-Temporal Truth   │ Chronological history without data amnesia.   │
└────────────────────────┴───────────────────────────────────────────────┘
```

---

## 2. The Tripartite Interaction Model

Baby LLM orchestrates cognitive data flow across three specialized interaction modalities:

```text
┌────────────────────────────────────────────────────────────────────────┐
│               THE TRIPARTITE INTERACTION ARCHITECTURE                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. EXTERNAL AGENT <──> MEMORY TOOL (Primary Substrate)                 │
│    • Protocol: FastMCP (stdio JSON-RPC) & FastAPI REST (/api/memories) │
│    • Clients: Cursor IDE, Claude Desktop, CrewAI, AutoGen, LangGraph   │
│    • Primitives: recall_memory(), commit_fact(), get_active_goals()    │
│    • Performance: Sub-30ms hybrid RRF recall; zero cloud leakage       │
├────────────────────────────────────────────────────────────────────────┤
│ 2. HUMAN <──> COMPANION CHAT (Direct User Surface)                     │
│    • Interface: Interactive Terminal CLI & Glass-Box Web Dashboard     │
│    • Capabilities: Real-time dialogue, Mindstream auditing, Morning    │
│      Readiness briefs, one-click fact deletion, and goal tracking      │
├────────────────────────────────────────────────────────────────────────┤
│ 3. INTERNAL MODEL <──> MODEL PROCESSING (Subconscious Engine)          │
│    • Engine: Local SLM (SmolLM2-1.7B / Qwen2.5-0.5B GGUF)              │
│    • Pipeline: Asynchronous REM Dream consolidation (15m idle / cron)  │
│    • Operations: SPO triple extraction, contradiction resolution,      │
│      Ebbinghaus decay curve evaluation, and YMYL protection floors     │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Substrate A: External Agent $\longleftrightarrow$ Memory Tool (Primary Focus)
Autonomous coding agents (Cursor IDE, Windsurf), reasoning assistants (Claude Desktop), and multi-agent orchestrators (CrewAI, LangGraph, AutoGen) require durable, structured memory across sessions. Baby LLM acts as their sovereign sidecar:
- **FastMCP Stdio Transport**: Native JSON-RPC tool calling without opening external network ports.
- **Agent Primitives**:
  - `recall_memory(query, top_k)`: Executes sub-30ms Reciprocal Rank Fusion over SQLite FTS5 (BM25) and LanceDB dense vectors.
  - `commit_fact(subject, predicate, object, category, ymyl)`: Directly injects verified facts into the bi-temporal knowledge graph with immediate conflict resolution.
  - `get_active_goals()`: Surfaces open commitments, deadlines, and active projects.
  - `record_daily_win(note)`: Commits completed accomplishments to the daily record.
- **REST Memory Bus**: For distributed or containerized agents, the FastAPI server exposes `/api/memories` and `/api/chat` over standard HTTP.

### 2.2 Substrate B: Human $\longleftrightarrow$ Companion Chat (Direct User Surface)
Human operators retain complete visibility and control over their memory substrate:
- **Interactive Terminal CLI (`baby-llm chat`)**: Provides zero-latency conversational companionship, gentle curiosity probes, and manual dream triggers.
- **Glass-Box Web Dashboard (`http://127.0.0.1:21225/`)**: Inspect the real-time Mindstream, filter memories by category, audit agent-created facts, and delete obsolete entries with a single click.
- **Personal Success Compass**: Daily Morning Readiness Briefs (07:30 AM) and Nightly Reflections (21:30 PM).

### 2.3 Substrate C: Internal Model $\longleftrightarrow$ Model Processing (Subconscious Engine)
Consolidating, restructuring, and decaying memories requires semantic reasoning. Performing this during an active agent tool call wastes tokens and introduces 3–8 second latency delays. 
- Baby LLM offloads all memory synthesis to an internal background SLM (`SmolLM2-1.7B` or `Qwen2.5-0.5B`).
- While the host machine is idle, this internal model executes model-to-model consolidation: analyzing raw dialogue logs, extracting structured facts, resolving historical contradictions, and archiving trivial banter.
- **Result**: External frontier agents (Claude 3.7 Sonnet, GPT-4o) never pay a token or latency tax for memory maintenance.

---

## 3. System Topology & Subsystem Interactions

The Baby LLM architecture spans four distinct vertical layers:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                       BABY LLM TOPOLOGY OVERVIEW                       │
└────────────────────────────────────────────────────────────────────────┘

 [External Agents & Clients]           [Human Interaction]
   • Cursor IDE / Claude Desktop         • Terminal CLI (baby-llm chat)
   • Autonomous Swarms (LangGraph)       • Glass-Box UI (Port 21225)
   • REST Clients (Python httpx)         • Bidirectional Obsidian Vault
          │                                     │
          ▼ (FastMCP stdio & REST)              ▼ (Interactive Prompt)
┌────────────────────────────────────────────────────────────────────────┐
│ DAYTIME FAST-PATH ENGINE (<30ms Latency Budget)                        │
│   ├─ Episodic Ring Buffer (deque: in-RAM sliding window)               │
│   ├─ Hybrid Retrieval (RRF: SQLite FTS5 BM25 + LanceDB BGE Vectors)    │
│   ├─ FastMCP Server (recall_memory, commit_fact, get_active_goals)     │
│   └─ Fast Inference (Embedded Qwen2.5-0.5B GGUF or Ollama Bridge)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼ [Zero-Blocking Append]
┌────────────────────────────────────────────────────────────────────────┐
│ WRITE-AHEAD INTERACTION LOG (WAL)                                      │
│   └─ SQLite Embedded Table: interaction_log (WAL Mode Enabled)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼ [Idle > 15m or 03:00 AM Cron]
┌────────────────────────────────────────────────────────────────────────┐
│ ASYNCHRONOUS REM DREAM CONSOLIDATION (Background Daemon)               │
│   ├─ Fact Extractor: Atomic SPO Triples & Confidence Scores            │
│   ├─ Conflict Resolver: Bi-Temporal Validity (valid_from / invalid)    │
│   ├─ Ebbinghaus Decay: R(t) = exp(-t / (S * I))                        │
│   └─ YMYL Shield: 100% Retention Floor for Health & Finance Facts      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PERSISTENT STORAGE & KNOWLEDGE SUBSTRATE                               │
│   ├─ Bi-Temporal Knowledge Graph (SQLite: memory_nodes & FTS5)         │
│   ├─ Dense Semantic Vector Store (LanceDB: memories table)             │
│   ├─ AES-GCM-256 Keyring Encryption (At-rest protection for YMYL)      │
│   ├─ Personal Success Compass (Morning Briefs & Commitment Tracker)    │
│   └─ Bidirectional Obsidian Vault Sync (Watchdog Markdown Observer)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. The 4-Tier Biological Memory Hierarchy

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
- **Bi-Temporal Property**: When a belief updates (*"We use PostgreSQL"* $	o$ *"We use SQLite"*), the outdated node is marked with `invalid_from = now`, the new node is committed with `valid_from = now`, and both records remain queryable for historical lineage reconstruction.

### Tier 4: Procedural Directives & Vault Markdown Sync
- **Implementation**: `src/baby_llm/runtime/context_assembler.py` and `src/baby_llm/sync/obsidian_sync.py`
- **Structure**: System persona prompts, daily morning summaries, and bidirectional Markdown files in `~/.baby_llm/vault/memories/<node_id>.md`.
- **Purpose**: Bridges structured database records into human-readable plain text files compatible with Obsidian, Logseq, or Git version control.

---

## 5. Runtime Execution Lifecycles

### 5.1 External Agent Memory Tool Pipeline (Fast Path)
When an external agent invokes `recall_memory(query)` or `commit_fact(...)`:
1. **Query Parsing**: FastMCP or REST extracts tool arguments.
2. **Hybrid Retrieval (<15ms)**:
   - BM25 search across SQLite FTS5 index (`memory_fts`).
   - FastEmbed 384-dimensional dense vector search in LanceDB.
   - Reciprocal Rank Fusion ($k=60$) ranks the top matching active memory nodes.
3. **Memory Reinforcement**: Each recalled node has its stability doubled ($S \leftarrow 2S$) to reflect active utility.
4. **Tool Return**: Instant formatted response returned to the agent loop (<18ms total overhead).

### 5.2 Real-Time Human Chat Pipeline
When a human chats via CLI or Web UI:
1. **Record Activity**: Immediately sets `self._pause_event` to yield compute from any running Dream Worker.
2. **Context Assembly (<20ms)**: Merges system persona, retrieved active memories, active goals, and episodic ring buffer.
3. **Inference**: Dispatches prompt to embedded Qwen2.5-0.5B GGUF or local Ollama.
4. **Append Log**: Writes turn to SQLite WAL (`interaction_log`) without blocking response streaming.

### 5.3 Asynchronous REM Dream Consolidation Pipeline
When idle timeout (>15m) or the nightly cron (03:00 AM) triggers:
1. **Idle Check**: Confirms zero user activity.
2. **Batch Ingestion**: Reads up to 50 un-processed turns from `interaction_log`.
3. **Fact Extraction (Internal SLM)**: Parses turns into atomic Subject-Predicate-Object triples with category tags.
4. **Conflict Resolution**: Identifies historical contradictions, marks old records invalid, and commits new nodes.
5. **Decay Evaluation**: Calculates retention $R(t) = \exp(-t / (S \cdot I))$. Nodes with $R(t) < 0.20$ (and not YMYL-shielded) are archived.
6. **Vector Sync**: Embeds active facts into LanceDB.

---

## 6. Concurrency, Threading, and Synchronization

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

## 7. Failure Modes & Resiliency Strategies

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
