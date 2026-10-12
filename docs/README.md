# 👶 Baby LLM: The Self-Evolving Local Memory & Life Success Engine

*Your 100% Offline Cognitive Companion, Second Brain, and Executive Accountability Partner*

[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Privacy: 100% Offline](https://img.shields.io/badge/Privacy-100%25%20Local-purple.svg)](getting-started.md)
[![Architecture: Hybrid RRF](https://img.shields.io/badge/Architecture-SQLite%20%2B%20LanceDB-orange.svg)](architecture.md)
[![Fast-Path: Sub--30ms](https://img.shields.io/badge/Latency-%3C30ms%20Fast--Path-brightgreen.svg)](core-engine.md)
[![Security: AES--GCM--256](https://img.shields.io/badge/Security-AES--GCM--256-red.svg)](configuration-and-storage.md)
[![MCP: Supported](https://img.shields.io/badge/MCP-Cursor%20%26%20Claude-cyan.svg)](interfaces-and-api.md)
[![Tests: 39 Passing](https://img.shields.io/badge/Tests-39%20Passed-success.svg)](development-and-testing.md)

---

## 🌟 What is Baby LLM?

Imagine an AI companion that **never sends a single byte to the cloud**, never forgets who you are when you open a new tab, and **actively helps you succeed in life**. 

Unlike conventional chatbots that suffer from permanent context amnesia or freeze your screen for 5 seconds while evaluating memories, **Baby LLM** operates like a living cognitive engine:
- **By Day ☀️**: It chats with zero perceptible lag (<30ms context assembly), pulling relevant facts from your local vector and full-text databases, and appends every interaction to a lightning-fast local log.
- **By Night 🌙**: While you sleep (or when you step away for 15 minutes), it enters a **"REM Dream" consolidation cycle**. A lightweight local model reviews your day, extracts durable facts into a knowledge graph, resolves contradictions, and archives trivial banter using scientific forgetting curves.

It starts as an **Infant** (curious, unbiased, asking gentle questions) and organically matures into an indispensable **Digital Twin**.

---

## 🧭 The Maturity Continuum

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      BABY LLM MATURITY CONTINUUM                       │
├─────────────────┬──────────────┬───────────────────────────────────────┤
│ Phase           │ Timeline     │ Cognitive Behaviors & Capabilities    │
├─────────────────┼──────────────┼───────────────────────────────────────┤
│ 1. Infancy      │ Days 1 - 7   │ High curiosity; gentle probes         │
│ 2. Toddler      │ Weeks 2 - 4  │ Routines & entity maps; style sync    │
│ 3. Apprentice   │ Months 2 - 6 │ Goal coaching; flags contradictions   │
│ 4. Digital Twin │ Year 1+      │ Proactive advisory; strategic counsel │
└─────────────────┴──────────────┴───────────────────────────────────────┘
```

---

## 💎 Core Merits: Why Baby LLM is a Game Changer

### 🛡️ 1. Absolute Privacy & Sovereign Data Ownership
- **Zero Cloud Leakage**: No telemetry, no API billing credits, and zero data streaming to external corporate servers.
- **At-Rest Hardware Encryption**: High-stakes personal data (bank details, health diagnoses, medications) is automatically encrypted with **AES-GCM-256** backed by your OS Keyring.
- **One-Click Erase**: Open the Glass-Box dashboard and instantly delete any memory node forever.

### ⚡ 2. Zero-Lag Daytime Fast Path (<30ms)
- Academic memory libraries force you to wait 3–8 seconds per prompt while an LLM synchronously evaluates facts.
- Baby LLM uses **Reciprocal Rank Fusion (RRF)** over SQLite FTS5 (BM25) and LanceDB dense vectors, compiling context in **<18ms** and appending turns to a SQLite Write-Ahead Log (WAL) in **<1ms**.

### 🧠 3. Bi-Temporal Truth (No Context Amnesia)
- When you update a belief (*"I lived in Seattle"* ➔ *"I moved to Austin"*), most systems delete the old fact.
- Baby LLM timestamps both: marking Seattle as invalid from today, and Austin as valid from today. Your entire life trajectory is preserved without confusion!

### 🌙 4. Asynchronous REM Dream Consolidation
- When your system is idle for 15 minutes or during the 03:00 AM nightly window, a background daemon reviews unprocessed dialogue turns.
- It parses raw turns into atomic Subject-Predicate-Object triples, embeds them into vector storage, and runs decay pruning without slowing down your active work.

### 🛡️ 5. Scientific Ebbinghaus Decay with YMYL Shield
- Trivial conversational banter (*"I ate a blueberry bagel today"*) naturally fades away over time via the exponential curve: $R(t) = \exp(-t / (S \cdot I))$.
- Critical life context (**YMYL**: Your Money or Your Life) is granted an **infinite retention floor ($R=1.0$)**. It will never forget your peanut allergy or mortgage bank!

### 🔌 6. Universal Model Context Protocol (MCP)
- Exposes your memory to **Cursor IDE** and **Claude Desktop** via stdio JSON-RPC. Query your life goals or commit project breakthroughs while coding!

### 📝 7. Bidirectional Obsidian / Markdown Vault Mirror
- Your memories aren't trapped in a proprietary black-box database. Baby LLM continuously mirrors active facts to `~/.baby_llm/vault/memories/*.md` with clean YAML frontmatter. Edit a note in Obsidian, and Baby LLM updates its knowledge graph in real time!

---

## 🎯 When is Baby LLM Invaluable?

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   THE DAY VS. NIGHT COGNITIVE CYCLE                    │
└────────────────────────────────────────────────────────────────────────┘

 [☀️ DAYTIME: Real-Time Fast Path (<30ms Latency Budget)]
   User Chat Prompt ──► Hybrid Retrieval (BM25 + LanceDB) ──► Instant Reply
                               │
                               ▼
        Instant Append to Write-Ahead Log (SQLite WAL Table)
                               │
                               ▼ [Inactivity > 15m OR 03:00 AM Cron]
 [🌙 NIGHTTIME: Asynchronous REM Dream Consolidation]
   Unprocessed Turns ──► Atomic SPO Triples ──► Contradiction Resolution
                               │
                               ▼
   Ebbinghaus Forgetting Curve ──► YMYL Retention Floor ──► Persistent DB
```

Here are real scenarios where Baby LLM completely outclasses cloud chatbots:

- ✈️ **The 35,000-Foot Nomad**: You are on an 11-hour flight with zero WiFi. Cloud chatbots are completely dead. Baby LLM runs 100% locally on your laptop, recalling all your notes, goals, and projects at full speed.
- 🤫 **The Confidential Executive & Stealth Founder**: You are preparing for sensitive salary negotiations, planning proprietary IP architecture, or managing company cash runway. You cannot paste this into cloud LLMs without violating corporate security policies. Baby LLM stays 100% on your local disk.
- 💊 **Personal Health & Medical Tracking**: Managing chronic symptom flare-ups, medication dosages, and medical histories. Cloud AI companies train on your prompts; Baby LLM locks your health records with AES-GCM-256 encryption.
- 💻 **Context-Aware Coding in Cursor / Claude**: While building a software project, ask Cursor: *"Recall what database conventions we agreed to last Tuesday"*. Baby LLM surfaces the exact memory node via MCP in milliseconds.
- 🌅 **Executive Focus & Overdue Accountability**: Every morning at 07:30 AM, Baby LLM reviews your commitments and delivers a concise 3-bullet Morning Readiness Brief, alerting you to dropped balls or overdue milestones.

---

## 🎬 Real-World Examples in Action

### 1. Moving Cities: Contradiction Resolution
```text
Day 1:
You      > I live in Seattle and work at Amazon as a distributed systems engineer.
Baby LLM > Noted! Seattle has great coffee, and distributed systems at Amazon is an exciting space.

[🌙 REM Dream runs: Extracts 'user lives_in Seattle' (valid_from: Day 1)]

Day 30:
You      > Big news! I relocated to Austin today to lead infrastructure at an AI startup.
Baby LLM > Congratulations on the move to Austin! Starting as infrastructure lead at a startup will be thrilling.

[🌙 REM Dream runs:
   - Sets 'user lives_in Seattle' -> invalid_from: Day 30 (Archived)
   - Sets 'user lives_in Austin'   -> valid_from: Day 30 (Active)
]

Day 35:
You      > Where do I currently live and what do I do?
Baby LLM > You currently live in Austin, Texas and lead infrastructure at an AI startup (having previously relocated from Seattle).
```

### 2. Medical Allergy & The YMYL Shield
```text
You      > Just left urgent care. Turns out I am severely allergic to penicillin.
Baby LLM > I'm glad you're safe! I have permanently registered your severe penicillin allergy with top priority.

[🌙 REM Dream runs:
   - Category: HEALTH | ymyl_protected: TRUE
   - Encrypted at rest via AES-GCM-256
   - Ebbinghaus decay curve ignored: Retention probability R(t) = 1.0 permanently.
]
```

### 3. The Gentle Curiosity Protocol
```text
You      > Tomorrow I need to finalize the deployment checklist for Project Valkyrie.
Baby LLM > Good plan. Ensuring deployment guardrails are locked in will prevent regression bugs.

           💭 By the way, you mentioned Project Valkyrie—is this an internal initiative or a client milestone?
```
*(Baby LLM asks at most **one** subtle question per session, never annoying you with constant interrogation).*

### 4. Morning Readiness Brief (07:30 AM)
```text
🌅 Good morning! Here is your Morning Readiness Brief:
• Priority 1: Launch Project Phoenix beta deployment (Due: Today).
• Priority 2: Complete code review for PR #126.
• Alert: Your commitment 'Draft investor update' was due 2 days ago.
• Protect your deep-work window from 09:00 to 12:00.
```

### 5. Universal MCP in Cursor IDE
When working in Cursor or Claude Desktop, you can ask directly:
```text
Cursor > @baby-llm recall_memory("Project Phoenix")
Baby LLM MCP >
- [GOAL] user goal_is launch Project Phoenix (Confidence: 95%, Source: hybrid)
- [WORK] user tech_stack FastAPI LanceDB SQLite (Confidence: 100%, Source: bm25)
```

---

## ⚡ High-Level System Architecture

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

## 📚 Documentation Architecture & File Index

This documentation suite is organized modularly to serve different engineering and user workflows. Each sub-document provides deep technical rigor and cross-references verified implementations:

| Document | Primary Focus & Coverage | Target Audience |
| :--- | :--- | :--- |
| **[getting-started.md](getting-started.md)** | Prerequisites (Python 3.11+), virtualenv installation, the 5 CLI launch modes, MCP setup, and first-run verification. | All Users & Developers |
| **[architecture.md](architecture.md)** | System topology, 4-tier memory hierarchy, runtime lifecycles, threading/concurrency models, and failure modes. | Systems Architects & AI Engineers |
| **[core-engine.md](core-engine.md)** | Sub-30ms fast-path assembler, hybrid RRF retrieval, REM dream consolidation cycle, Ebbinghaus decay math, and persona maturation. | Core Engine Contributors |
| **[configuration-and-storage.md](configuration-and-storage.md)** | Pydantic Settings, environment variables, SQLite WAL/FTS5 schemas, LanceDB tables, AES-GCM-256 encryption, and Obsidian vault sync. | Backend & Database Engineers |
| **[interfaces-and-api.md](interfaces-and-api.md)** | Interactive CLI commands, FastAPI REST specification (Port 21225), Model Context Protocol (MCP) tools, and Web UI. | Frontend & Integration Engineers |
| **[development-and-testing.md](development-and-testing.md)** | Local development setup, 39-test pytest execution, mocking strategies, common troubleshooting, and subsystem extension guides. | QA Engineers & Maintainers |

---

## 🧭 Audience-Tailored Reading Paths

Depending on your role and objectives, follow these recommended reading sequences:

### Path A: End User & Local Operator 👤
*Goal: Install Baby LLM, configure local inference, interact via Web UI or Terminal, and connect to Cursor/Claude.*
1. **[getting-started.md](getting-started.md)**: Follow setup steps, create the virtual environment, install dependencies, and run your first chat session.
2. **[interfaces-and-api.md](interfaces-and-api.md)**: Learn CLI subcommands (`chat`, `serve`, `ui`, `dream`, `memories`), explore the Glass-Box dashboard, and configure the MCP server in Claude Desktop or Cursor.
3. **[configuration-and-storage.md](configuration-and-storage.md)**: Configure environment overrides (`.env`), set custom models or ports, and connect your Obsidian notes vault.

### Path B: Core Systems & AI Engineer 🛠️
*Goal: Understand memory consolidation, hybrid retrieval performance, bi-temporal graph semantics, and mathematical forgetting curves.*
1. **[architecture.md](architecture.md)**: Study the 4-tier biological memory hierarchy, thread concurrency model, and daytime vs. nighttime execution boundaries.
2. **[core-engine.md](core-engine.md)**: Inspect the mathematical formulation of the Ebbinghaus decay curve, the Reciprocal Rank Fusion algorithm, and the bi-temporal conflict resolution logic.
3. **[configuration-and-storage.md](configuration-and-storage.md)**: Review SQLite FTS5 virtual table schemas, synchronization triggers, LanceDB PyArrow definitions, and AES-GCM-256 OS Keyring encryption.
4. **[development-and-testing.md](development-and-testing.md)**: Run the 39-test suite, review unit/integration test gates, and inspect extension points.

### Path C: Interface & Ecosystem Integrator 🔌
*Goal: Build external clients, integrate custom IDE plugins via MCP, connect local applications via REST, or extend the Web dashboard.*
1. **[interfaces-and-api.md](interfaces-and-api.md)**: Deep dive into the FastAPI REST API specifications, query parameters, request/response JSON contracts, and MCP tool declarations.
2. **[configuration-and-storage.md](configuration-and-storage.md)**: Understand the YAML frontmatter schema for bidirectional Markdown synchronization and SQLite tables.
3. **[development-and-testing.md](development-and-testing.md)**: Run integration tests (`test_api_server.py`, `test_mcp_server.py`) and learn how to extend REST endpoints and MCP tools.

---

## 📊 System Feature Matrix

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

## 🧪 Verification Status & Test Coverage

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

For complete testing instructions, troubleshooting, and extensions, refer to **[development-and-testing.md](development-and-testing.md)**.
