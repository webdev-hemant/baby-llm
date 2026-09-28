# 👶 Baby LLM
*The Privacy-First, Self-Evolving Local Memory & Life Success Engine*

[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Privacy: 100% Offline](https://img.shields.io/badge/Privacy-100%25%20Local-purple.svg)](#privacy--data-sovereignty)
[![Architecture: Hybrid RRF](https://img.shields.io/badge/Architecture-SQLite%20%2B%20LanceDB-orange.svg)](#system-architecture)
[![MCP: Supported](https://img.shields.io/badge/MCP-Compatible-cyan.svg)](#universal-mcp-server)

**Baby LLM** is an autonomous, local-first cognitive companion designed to run completely offline on consumer hardware with **zero latency overhead (< 30ms)** on the real-time chat path.

Unlike conventional chatbots that suffer from context amnesia or stream private thoughts to cloud APIs, Baby LLM starts as an infant (high curiosity, clean slate) and organically matures into an indispensable personal confidant and life success manager.

---

## 🧭 The Maturity Continuum

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BABY LLM MATURITY CONTINUUM                         │
├─────────────────┬──────────────────┬───────────────────┬────────────────────┤
│  1. INFANCY     │  2. TODDLER      │  3. APPRENTICE    │  4. DIGITAL TWIN   │
│  (Days 1 - 7)   │  (Weeks 2 - 4)   │  (Months 2 - 6)   │  (Year 1+)         │
├─────────────────┼──────────────────┼───────────────────┼────────────────────┤
│ • High Curiosity│ • Recognizes     │ • Anticipates     │ • High-fidelity    │
│ • Gentle probing│   patterns &     │   needs & goals   │   cognitive sync   │
│   questions     │   routines       │ • Flags personal  │ • Proactive        │
│ • Builds initial│ • Calibrates     │   contradictions  │   advisory &       │
│   identity graph│   response style │ • Accountability  │   strategic counsel│
│ • Learns voice  │ • Maps entities  │   watchdog        │ • Lifelong memory  │
└─────────────────┴──────────────────┴───────────────────┴────────────────────┘
```

---

## ⚡ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BABY LLM RUNTIME TOPOLOGY                          │
└─────────────────────────────────────────────────────────────────────────────┘

                  ┌─────────────────────────────────────────┐
                  │           USER INTERFACES               │
                  │  • Glass-Box Web Dashboard              │
                  │  • Interactive Terminal CLI             │
                  │  • Cursor IDE & Claude Desktop (MCP)    │
                  └────────────────────┬────────────────────┘
                                       │
                      User Prompt /    │ Streaming Response
                      Context Query    │ (< 30ms fast-path overhead)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. DAYTIME FAST-PATH ENGINE (Real-Time, Zero-Lag)                           │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Working Context Assembler                                           │   │
│   │  • Episodic Ring Buffer: Last 10-15 conversation turns              │   │
│   │  • Hybrid Sub-20ms Retrieval:                                       │   │
│   │      - BM25 Full-Text Search (SQLite FTS5) for exact keywords       │   │
│   │      - Dense Vector Search (LanceDB + BGE-Small-EN-v1.5 ONNX)       │   │
│   │  • Active Identity & Success Directives Injection                   │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│                  Local Inference Engine (Ollama / llama.cpp)                │
│                  Models: Llama 3.2 3B / Qwen 2.5 7B / Mistral Nemo          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                      Instant Append   │ (Zero-blocking write to WAL)
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
│   │ Quantized SLM Worker (SmolLM2-1.7B-Q4 / Qwen2.5-1.5B-Q4)            │   │
│   │  • Fact Extraction: Subject-Predicate-Object (SPO) Triples         │   │
│   │  • Bi-Temporal Resolution: Updates valid_from / invalid_from        │   │
│   │  • Ebbinghaus Decay: R(t) = exp(-t / (S * I))                       │   │
│   │  • YMYL Protection: Infinite retention floor for health/finance     │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│          Bi-Temporal Relational Graph (SQLite) & Vector Store (LanceDB)      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. PERSONAL SUCCESS COMPASS & ECOSYSTEM SYNC                                │
│    • Morning Intention (07:30) & Evening Reflection (21:30) Loops           │
│    • Universal MCP Server (recall_memory, commit_fact, get_active_goals)    │
│    • Bidirectional Obsidian / Local Markdown Vault Synchronization          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

* **Zero-Lag Fast Path (< 30ms)**: Memory retrieval uses hybrid Reciprocal Rank Fusion (SQLite FTS5 BM25 + LanceDB SIMD vectors) without slowing conversational flow.
* **Bi-Temporal Knowledge Graph**: Tracks both *when a fact happened* and *when it was learned*. Contradictions (e.g. moving from Seattle to Austin) archive the prior state while preserving full chronological trajectory.
* **REM Dream Consolidation**: When the user is idle, a sub-2B SLM (`SmolLM2-1.7B` using < 800MB VRAM) extracts facts and resolves conflicts without freezing daytime chat.
* **Ebbinghaus Decay with YMYL Shield**: Trivial banter fades over time via scientific decay curves, while critical facts (Health, Finance, Core Values) receive an infinite retention floor.
* **Proactive Life Success Engine**:
  * **07:30 AM Morning Intention Brief**: Surfaces top 2 needle-moving priorities.
  * **Gentle Curiosity Protocol**: Asks at most **one** subtle clarifying question per session when ambiguous projects or entities are introduced.
  * **Accountability Watchdog**: Detects dropped commitments and overdue goals.
  * **09:30 PM Nightly Reflection**: Frictionless brain dump and wins capture.
* **Universal Model Context Protocol (MCP)**: Seamlessly integrates personal memory into Cursor IDE and Claude Desktop.
* **Glass-Box Control**: Complete visual transparency—inspect, edit, pin, or one-click erase any memory node from the dashboard.

---

## 📦 Quickstart & Installation

### 1. Prerequisites
- **Python 3.11+**
- **Ollama** installed and running locally (`ollama run llama3.2:3b` or `ollama run qwen2.5:7b`)

### 2. Environment Setup
```bash
# Clone or navigate to the repository
cd /Users/admin/Desktop/corporate/projects/baby-llm

# Create virtual environment and install dependencies
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e .
```

---

## 🎮 Running Baby LLM

### 1. Interactive Terminal Chat
Chat directly with Baby LLM from your command line:
```bash
.venv/bin/python -m baby_llm.cli chat
```
*Special commands in chat:*
- `/dream` — Manually trigger a REM Dream consolidation cycle.
- `exit` — Exit the companion session.

### 2. Launch FastAPI Server & Glass-Box Dashboard
Start the local REST server and open the web dashboard:
```bash
.venv/bin/python -m baby_llm.cli serve --port 8000
```
Open **[http://127.0.0.1:8000/ui/](http://127.0.0.1:8000/ui/)** in your browser to access:
- **Interactive Companion**: Chat with memory attribution indicators.
- **Mindstream Vault**: Inspect categorized facts, confidence ratings, and stability scores.
- **Bi-Temporal Timeline**: Visual historical trajectory of evolving facts.
- **Success Compass**: Morning briefs, active commitments, and accountability tracking.

### 3. Run Universal MCP Server
Expose Baby LLM tools to Claude Desktop, Cursor, or any MCP client:
```bash
.venv/bin/python -m baby_llm.cli mcp
```

### 4. Trigger REM Dream Cycle via CLI
```bash
.venv/bin/python -m baby_llm.cli dream
```

### 5. Inspect Active Memories via CLI
```bash
.venv/bin/python -m baby_llm.cli memories
```

---

## 🔌 Universal MCP Server Configuration

Connect Baby LLM memory to **Cursor IDE** or **Claude Desktop** by updating your configuration file:

### Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "baby-llm": {
      "command": "/Users/admin/Desktop/corporate/projects/baby-llm/.venv/bin/python",
      "args": ["-m", "baby_llm.cli", "mcp"]
    }
  }
}
```

### Cursor (`Cursor Settings -> Features -> MCP -> Add New MCP Server`)
- **Name**: `baby-llm`
- **Type**: `command`
- **Command**: `/Users/admin/Desktop/corporate/projects/baby-llm/.venv/bin/python -m baby_llm.cli mcp`

#### Exposed MCP Tools:
| Tool | Description |
| :--- | :--- |
| `recall_memory(query, top_k)` | Retrieves verified personal context matching a query. |
| `commit_fact(subject, predicate, object, category, ymyl)` | Explicitly commits or updates a fact in the bi-temporal graph. |
| `get_active_goals()` | Lists open goals, commitments, and deadlines. |
| `record_daily_win(note)` | Captures an accomplishment or breakthrough for the day. |

---

## 📁 Project Directory Structure

```text
baby-llm/
├── docs/
│   └── baby-llm-reasearch/
│       ├── baby_llm_product_blueprint.md    # Master architectural specification
│       └── local_llm_memory_research.md     # SOTA benchmark & framework analysis
├── implementation/
│   └── baby-llm/
│       └── IMPLEMENTATION_PLAN.md           # 12-week development roadmap & verification
├── src/
│   └── baby_llm/
│       ├── config.py                        # Pathing & environment configuration
│       ├── cli.py                           # CLI entry points (chat, dream, serve, mcp)
│       ├── core/
│       │   ├── models.py                    # Pydantic schemas (MemoryNode, Turn, Goal)
│       │   └── ring_buffer.py               # In-memory episodic buffer
│       ├── storage/
│       │   ├── db.py                        # SQLite WAL & FTS5 full-text schema
│       │   ├── wal.py                       # Sub-millisecond interaction logger
│       │   ├── graph_store.py               # Bi-temporal SPO graph CRUD
│       │   └── vector_store.py              # LanceDB disk-native vector index
│       ├── retrieval/
│       │   ├── embedder.py                  # ONNX fast local embedding (BGE-Small)
│       │   ├── bm25.py                      # SQLite FTS5 exact search
│       │   └── hybrid.py                    # Reciprocal Rank Fusion (RRF) retriever
│       ├── runtime/
│       │   ├── context_assembler.py         # Sub-20ms prompt compiler
│       │   └── ollama_client.py             # Local Ollama streaming client
│       ├── dream/
│       │   ├── worker.py                    # Background REM consolidation loop
│       │   ├── extractor.py                 # Sub-2B SLM atomic fact parser
│       │   ├── resolver.py                  # Bi-temporal contradiction resolver
│       │   └── decay.py                     # Ebbinghaus decay & YMYL evaluator
│       ├── success/
│       │   ├── agent.py                     # Morning brief & evening reflection
│       │   ├── tracker.py                   # Commitments & goals state machine
│       │   └── curiosity.py                 # Gentle Curiosity Protocol
│       ├── mcp/
│       │   └── server.py                    # Model Context Protocol stdio/SSE server
│       ├── sync/
│       │   └── obsidian_sync.py             # Watchdog bidirectional Markdown sync
│       └── api/
│           └── server.py                    # FastAPI local REST & WebUI server
├── ui/                                      # Glass-Box Web Dashboard
│   ├── index.html                           # Modern dashboard interface
│   ├── styles.css                           # Glassmorphic dark design system
│   └── app.js                               # Frontend state & API integration
├── tests/
│   ├── unit/                                # Unit test suite
│   └── integration/                         # End-to-end integration tests
├── pyproject.toml
└── README.md
```

---

## 🧪 Testing & Verification

Baby LLM maintains a complete unit and integration test suite:

```bash
.venv/bin/pytest -v
```

### Verified Test Gates:
- ✅ **WAL Interaction Logging**: Verifies non-blocking writes and dream processing flags.
- ✅ **Bi-Temporal Invalidation**: Validates conflict resolution and timeline retention.
- ✅ **Ebbinghaus Decay Formula**: Confirms mathematical decay and stability doubling.
- ✅ **YMYL Immunity Floor**: Ensures 100% retention on health and finance facts.
- ✅ **Hybrid Retrieval (RRF)**: Verifies exact BM25 matches combined with dense vector ranks.
- ✅ **End-to-End REM Dream Cycle**: Full pipeline from raw dialogue to contradiction resolution.
- ✅ **FastAPI REST Endpoints**: Full lifecycle testing for memory and success APIs.

---

## 🔒 Privacy & Data Sovereignty

* **Zero Cloud Inference**: All embeddings (BGE-Small-EN ONNX) and LLM inference (Ollama) run 100% on your local CPU / GPU.
* **Encrypted at Rest**: High-stakes YMYL data is isolated and protected.
* **No Telemetry**: Absolutely zero diagnostic pings, analytics, or external network requests.
* **Complete User Sovereignty**: You own your SQLite and LanceDB files locally (`~/.baby_llm/`). Erase or export any record at any time with a single click.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
