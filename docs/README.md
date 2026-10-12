# 👶 Baby LLM Technical Documentation Portal

*Production Architecture, Cognitive Systems, Storage Specifications, and Developer Reference*

---

## 1. Executive Overview & Mission

**Baby LLM** is an autonomous, 100% offline, privacy-first local memory and cognitive companion engine. Engineered for local execution on standard consumer hardware, it guarantees zero cloud API dependencies, zero external network telemetry, and sub-30ms context assembly latency on real-time conversational paths.

Conventional conversational AI platforms suffer from two fatal extremes:
1. **Cloud Surveillance & Context Amnesia**: Centralized cloud chatbots stream user thoughts, financial queries, and medical records to remote servers while resetting context across disparate conversation threads.
2. **Synchronous Memory Latency Tax**: Academic and experimental memory frameworks execute heavyweight multi-turn LLM extraction calls synchronously on every user turn, freezing conversational flow for several seconds.

Baby LLM resolves this dilemma through a **bifurcated cognitive architecture**:
- **Daytime Fast-Path Engine (<30ms Overhead)**: Assembles working episodic context, executes Reciprocal Rank Fusion (RRF) over SQLite FTS5 and LanceDB vector indices, and feeds local inference (`Qwen2.5-0.5B` embedded or `Ollama`) with zero user-perceptible delay. Every turn is appended in sub-millisecond time to an embedded SQLite Write-Ahead Log (WAL).
- **Asynchronous REM Dream Consolidation**: When the user is idle (>15 minutes) or during a nightly 03:00 AM cron window, a background daemon processes unflagged interaction logs, extracts atomic Subject-Predicate-Object (SPO) knowledge triples, resolves chronological contradictions via bi-temporal validity windows, and applies Ebbinghaus forgetting curves with strict YMYL (Your Money or Your Life) retention floors.

---

## 2. High-Level System Architecture

The following diagram illustrates the end-to-end data flow and subsystem topology of Baby LLM:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                       BABY LLM TOPOLOGY OVERVIEW                       │
└────────────────────────────────────────────────────────────────────────┘

 [User Interfaces]
   ├─ Glass-Box Web UI (http://127.0.0.1:21225)
   ├─ Terminal CLI (baby-llm chat / dream / memories)
   └─ Universal MCP Server (Cursor IDE & Claude Desktop)
         │
         ▼
┌────────────────────────────────────────────────────────────────────────┐
│ DAYTIME FAST-PATH ENGINE (<30ms Latency Budget)                        │
│   ├─ Episodic Ring Buffer (deque: last 15 conversation turns)          │
│   ├─ Hybrid Retrieval (RRF: SQLite FTS5 BM25 + LanceDB BGE Vectors)    │
│   ├─ Context Assembler (Persona + Active Memories + Commitments)       │
│   └─ Unified Inference (Embedded Qwen2.5-0.5B or Ollama Llama 3.2)     │
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
│ PERSISTENT STORAGE & EXTERNAL ECOSYSTEM                                │
│   ├─ Bi-Temporal Knowledge Graph (SQLite: memory_nodes & FTS5)         │
│   ├─ Dense Semantic Vector Store (LanceDB: memories table)             │
│   ├─ AES-GCM-256 Keyring Encryption (At-rest protection for YMYL)      │
│   ├─ Personal Success Compass (Morning Briefs & Commitment Tracker)    │
│   └─ Bidirectional Obsidian Vault Sync (Watchdog Markdown Observer)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Documentation Architecture & File Index

This documentation suite is organized modularly to serve different engineering workflows. Each document is exhaustive, self-contained, and cross-linked to verified implementations within `src/baby_llm/`, `ui/`, and `tests/`.

| Document | Primary Focus & Coverage | Target Audience |
| :--- | :--- | :--- |
| [getting-started.md](getting-started.md) | Prerequisites (Python 3.11+), virtualenv installation, CLI commands, server launch, MCP setup, and first-run verification. | All Users & Developers |
| [architecture.md](architecture.md) | System topology, 4-tier memory hierarchy, runtime lifecycle, threading/concurrency models, and failure modes. | Systems Architects & AI Engineers |
| [core-engine.md](core-engine.md) | Sub-30ms fast-path assembler, hybrid RRF retrieval, REM dream consolidation cycle, Ebbinghaus decay math, and persona maturation. | Core Engine Contributors |
| [configuration-and-storage.md](configuration-and-storage.md) | Pydantic Settings, environment variables, SQLite WAL/FTS5 schemas, LanceDB tables, AES-GCM-256 encryption, and Obsidian vault sync. | Backend & Database Engineers |
| [interfaces-and-api.md](interfaces-and-api.md) | Interactive CLI commands, FastAPI REST specification (Port 21225), Model Context Protocol (MCP) tools, and Web UI. | Frontend & Integration Engineers |
| [development-and-testing.md](development-and-testing.md) | Local development setup, 39-test pytest execution, mocking strategies, common troubleshooting, and subsystem extension guides. | QA Engineers & Maintainers |

---

## 4. Audience-Tailored Reading Paths

Depending on your role and objectives, follow these recommended reading sequences:

### Path A: End User & Local Operator
*Goal: Install Baby LLM, configure local inference, interact via Web UI or Terminal, and connect to Cursor/Claude.*
1. **[getting-started.md](getting-started.md)**: Follow setup steps, create the virtual environment, install dependencies, and run your first chat session.
2. **[interfaces-and-api.md](interfaces-and-api.md)**: Learn CLI subcommands (`chat`, `serve`, `ui`, `dream`, `memories`), explore the Glass-Box dashboard, and configure the MCP server in Claude Desktop or Cursor.
3. **[configuration-and-storage.md](configuration-and-storage.md)**: Configure environment overrides (`.env`), set custom models or ports, and connect your Obsidian notes vault.

### Path B: Core Systems & AI Engineer
*Goal: Understand memory consolidation, hybrid retrieval performance, bi-temporal graph semantics, and mathematical forgetting curves.*
1. **[architecture.md](architecture.md)**: Study the 4-tier biological memory hierarchy, thread concurrency model, and daytime vs. nighttime execution boundaries.
2. **[core-engine.md](core-engine.md)**: Inspect the mathematical formulation of the Ebbinghaus decay curve, the Reciprocal Rank Fusion algorithm, and the bi-temporal conflict resolution logic.
3. **[configuration-and-storage.md](configuration-and-storage.md)**: Review SQLite FTS5 virtual table schemas, synchronization triggers, LanceDB PyArrow definitions, and AES-GCM-256 OS Keyring encryption.
4. **[development-and-testing.md](development-and-testing.md)**: Run the 39-test suite, review unit/integration test gates, and inspect extension points.

### Path C: Interface & Ecosystem Integrator
*Goal: Build external clients, integrate custom IDE plugins via MCP, connect local applications via REST, or extend the Web dashboard.*
1. **[interfaces-and-api.md](interfaces-and-api.md)**: Deep dive into the FastAPI REST API specifications, query parameters, request/response JSON contracts, and MCP tool declarations.
2. **[configuration-and-storage.md](configuration-and-storage.md)**: Understand the YAML frontmatter schema for bidirectional Markdown synchronization and SQLite tables.
3. **[development-and-testing.md](development-and-testing.md)**: Run integration tests (`test_api_server.py`, `test_mcp_server.py`) and learn how to extend REST endpoints and MCP tools.

---

## 5. System Feature Matrix

The following table summarizes the implementation specifications across all core subsystems:

| Subsystem | Underlying Technology | Verified Capabilities & Performance Targets |
| :--- | :--- | :--- |
| **Fast-Path Chat** | `ContextAssembler` + `UnifiedLLMProvider` | <30ms assembly overhead; zero-blocking WAL write; automatic fallback from Embedded Qwen to Ollama. |
| **Episodic Buffer** | `EpisodicRingBuffer` (Python `deque`) | Stores last 15 interaction turns in active RAM for immediate conversational continuity. |
| **Full-Text Search** | SQLite FTS5 (`porter unicode61`) | Sub-5ms lexical matching across `subject`, `predicate`, and `object` with automatic trigger synchronization. |
| **Dense Vector Index** | LanceDB + FastEmbed (`bge-small-en-v1.5`) | 384-dimensional dense semantic search using SIMD-accelerated cosine distance; filterable by active state. |
| **Hybrid Ranking** | Reciprocal Rank Fusion (`HybridRetriever`) | $k=60$ constant; combines lexical and semantic ranks; automatically reinforces retrieved nodes ($S \leftarrow 2S$). |
| **Consolidation** | `DreamWorker` (Background Thread) | Monitors 15m idle timeout and 03:00 AM cron; extracts SPO triples; automatically pauses upon user activity. |
| **Conflict Engine** | `ConflictResolver` (Bi-Temporal) | Tracks `valid_from` and `invalid_from`; updates facts without history loss; preserves complete audit trajectories. |
| **Memory Decay** | `EbbinghausDecayEngine` | $R(t) = \exp(-t / (S \cdot I))$; category-weighted importance; infinite retention floor for YMYL health/finance. |
| **Data Encryption** | `YMYLEncryptionManager` (AES-GCM-256) | Attribute-level encryption of sensitive facts at rest; backed by OS Keyring with `0600` local file fallback. |
| **Success Compass** | `PersonalSuccessAgent` + `SuccessTracker` | 07:30 AM Morning Brief with SQLite caching; 21:30 PM Nightly Reflection; accountability watchdog for overdue goals. |
| **Gentle Curiosity** | `GentleCuriosityEngine` | At most 1 subtle clarifying probe per session; detects ambiguous entities (`project <name>`) without annoying users. |
| **Universal MCP** | FastMCP (`baby-llm-mcp`) | Stdio transport exposing `recall_memory`, `commit_fact`, `get_active_goals`, and `record_daily_win`. |
| **Glass-Box UI** | Vanilla JS + Glassmorphic CSS | PWA standalone dashboard on Port 21225 (`B-A-B-Y`); Mindstream inspector, Timeline visualizer, one-click erase. |
| **Vault Sync** | `VaultSyncManager` + `watchdog` | Bidirectional synchronization between SQLite graph and local Markdown/Obsidian files with YAML frontmatter. |

---

## 6. Verification Status & Test Coverage

All technical specifications documented in this portal are actively validated by an automated test suite:

- **Total Test Cases**: 39 passing tests (0 failures, 0 skipped).
- **Execution Time**: ~12.7 seconds on standard developer hardware.
- **Test Categories**:
  - 10 Unit Test Suites (`tests/unit/`): WAL logging, graph operations, bi-temporal invalidation, Ebbinghaus decay formulas, AES-GCM encryption, hybrid RRF retrieval, curiosity limits, commitment state machine, CLI subparsers, and vault sync.
  - 3 Integration Test Suites (`tests/integration/`): End-to-end REM dream consolidation, FastAPI REST endpoints, and MCP tool workflows.

To execute the test suite, run:
```bash
.venv/bin/pytest -v
```

For complete testing instructions and troubleshooting steps, refer to [development-and-testing.md](development-and-testing.md).
