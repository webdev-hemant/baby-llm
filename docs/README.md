# 👶 Baby LLM: Sovereign Long-Term Memory Engine & Cognitive Companion

*100% Offline Memory Tool for Autonomous AI Agents, Human Companion, and Self-Evolving Second Brain*

[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Privacy: 100% Offline](https://img.shields.io/badge/Privacy-100%25%20Local-purple.svg)](getting-started.md)
[![Primary Interface: FastMCP](https://img.shields.io/badge/Interface-FastMCP%20%26%20REST-cyan.svg)](interfaces-and-api.md)
[![Fast-Path: Sub--30ms](https://img.shields.io/badge/Latency-%3C30ms%20Fast--Path-brightgreen.svg)](core-engine.md)
[![Architecture: Hybrid RRF](https://img.shields.io/badge/Architecture-SQLite%20%2B%20LanceDB-orange.svg)](architecture.md)
[![Security: AES--GCM--256](https://img.shields.io/badge/Security-AES--GCM--256-red.svg)](configuration-and-storage.md)
[![Tests: 39 Passing](https://img.shields.io/badge/Tests-39%20Passed-success.svg)](development-and-testing.md)

---

## 🌟 What is Baby LLM?

Most AI agents today (Cursor IDE, Claude Desktop, Windsurf, LangGraph, CrewAI) suffer from a crippling flaw: **ephemeral context amnesia**. Every session begins as a blank slate. When developers try to grant agents long-term memory, they typically resort to cloud memory SaaS that:
- ❌ Streams proprietary codebase architecture, API secrets, and personal notes to third-party cloud servers.
- ❌ Imposes 1–3 second latency penalties per tool retrieval, stalling iterative agent loops.
- ❌ Wastes expensive frontier model tokens asking the agent to manually extract, organize, and prune memories.
- ❌ Erases historical context when beliefs change, leading to contradictory hallucination.

**Baby LLM** solves this fundamentally by providing a **100% sovereign, local long-term memory engine and cognitive tool substrate**. It is architected around three complementary interaction pillars:

1. 🤖 **External Agent $\longleftrightarrow$ Memory Tool (Primary Focus)**:
   A high-speed, local long-term memory tool for external AI agents (Cursor IDE, Claude Desktop, AutoGen, CrewAI, LangGraph, custom agent loops). Exposes clean FastMCP tools (`recall_memory`, `commit_fact`, `get_active_goals`, `record_daily_win`) and a FastAPI REST API (`/api/memories`). Queries execute in **<30ms** via local Reciprocal Rank Fusion (SQLite FTS5 + LanceDB dense vectors), without cloud dependencies, API credit burn, or data leakage.
2. 👤 **Human $\longleftrightarrow$ Companion Chat (Direct Human Surface)**:
   A zero-lag conversational companion accessible via terminal CLI (`baby-llm chat`) or Glass-Box Web Dashboard (`http://127.0.0.1:21225/`). The human operator has 100% transparency: inspect what memories external agents have stored, edit or delete facts, receive executive Morning Readiness Briefs (07:30 AM), and explore personal mindstreams.
3. 🧠 **Internal Model $\longleftrightarrow$ Model Processing (Subconscious Engine)**:
   An autonomous background REM Dream cycle powered by an embedded local Small Language Model (SLM: `SmolLM2-1.7B` or `Qwen2.5-0.5B`). While the host machine is idle, the internal model reads raw interaction logs from SQLite WAL, extracts atomic Subject-Predicate-Object triples, resolves bi-temporal contradictions, and applies Ebbinghaus forgetting decay curves. **External agents never have to waste prompt tokens or execution cycles doing memory cleanup!**

---

## 🧭 The Tripartite Interaction Model

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

---

## 🧭 The Maturity Continuum

As memories accumulate and consolidate, Baby LLM organically evolves from a curious infant into an indispensable digital twin:

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

### 🤖 1. Dedicated Agent Memory Substrate (FastMCP & REST API)
- Connect any AI coding agent (**Cursor IDE**, **Claude Desktop**, **Windsurf**) or multi-agent orchestrator (**CrewAI**, **LangGraph**, **AutoGen**) directly to Baby LLM.
- Stdio FastMCP tools (`recall_memory`, `commit_fact`, `get_active_goals`, `record_daily_win`) allow agents to recall verified context and commit breakthroughs in real time.

### ⚡ 2. Zero-Lag Daytime Fast Path (<30ms for Agent Tool Calls)
- Academic memory libraries force agents to wait 3–8 seconds per tool call while an LLM synchronously evaluates facts.
- Baby LLM uses **Reciprocal Rank Fusion (RRF)** over SQLite FTS5 (BM25) and LanceDB dense vectors, compiling context in **<18ms** and appending turns to a SQLite Write-Ahead Log (WAL) in **<1ms**.

### 🌙 3. Autonomous Model-to-Model Dream Processing (Zero Agent Token Tax)
- Frontier agents (Claude 3.7 Sonnet, GPT-4o) are expensive. Asking them to summarize, index, and deduplicate memories on every turn burns tokens rapidly.
- Baby LLM delegates consolidation to an offline local Small Language Model (SLM) that runs while your machine is idle, extracting SPO triples and updating vector embeddings for free.

### 🛡️ 4. Absolute Privacy & Sovereign Data Ownership
- **Zero Cloud Leakage**: No telemetry, no API billing credits, and zero data streaming to external corporate servers.
- **At-Rest Hardware Encryption**: High-stakes personal data (bank details, health diagnoses, medications) is automatically encrypted with **AES-GCM-256** backed by your OS Keyring.

### 🧠 5. Bi-Temporal Truth (No Context Amnesia)
- When project architecture changes (*"We used PostgreSQL"* ➔ *"We migrated to SQLite + LanceDB"*), most systems overwrite the old fact.
- Baby LLM timestamps both: marking PostgreSQL as invalid from today, and SQLite as valid from today. Agents can trace architectural history without confusion!

### 📉 6. Scientific Ebbinghaus Decay with YMYL Shield
- Trivial conversational banter naturally fades away over time via the exponential curve: $R(t) = \exp(-t / (S \cdot I))$.
- Critical life context (**YMYL**: Your Money or Your Life) is granted an **infinite retention floor ($R=1.0$)**. It will never forget your medical allergies or core project constraints.

### 🪟 7. Glass-Box Human Control & Obsidian Vault Sync
- Memories aren't locked in a black-box database. Open the Glass-Box dashboard (`http://127.0.0.1:21225/`) to view the Mindstream and delete nodes with one click.
- Active facts continuously mirror to `~/.baby_llm/vault/memories/*.md` with clean YAML frontmatter for seamless Obsidian integration.

---

## 🎯 When is Baby LLM Invaluable?

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   THE DAY VS. NIGHT COGNITIVE CYCLE                    │
└────────────────────────────────────────────────────────────────────────┘

 [☀️ DAYTIME: Real-Time Fast Path (<30ms Latency Budget)]
   Agent / User Prompt ──► Hybrid Retrieval (BM25 + LanceDB) ──► Instant Context
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

Here are real scenarios where Baby LLM completely outclasses cloud memory services:

- 💻 **Context-Aware Coding in Cursor & Claude**: While building software in Cursor, your agent queries: `recall_memory("Project Phoenix architecture")`. Baby LLM surfaces the exact schema and conventions in <18ms, preventing repetitive explanations across sessions.
- 🐝 **Multi-Agent Swarms with Shared Sovereign Memory**: Autonomous agent loops (LangGraph, CrewAI) read from and write to Baby LLM as a shared local memory bus. Agents share durable context across runs without cloud bills.
- ✈️ **The 35,000-Foot Nomad**: You are on an 11-hour flight with zero WiFi. Cloud AI tools are completely dead. Baby LLM runs 100% locally on your laptop, recalling all your notes, goals, and projects at full speed.
- 🤫 **Confidential IP & Stealth Operations**: You are architecting sensitive proprietary software or managing financial runway. You cannot paste this into cloud LLMs. Baby LLM stays 100% on your local disk.
- 💊 **Personal Health & Medical Tracking**: Tracking medical dosages, symptoms, and health history. Cloud AI companies train on your prompts; Baby LLM locks your health records with AES-GCM-256 encryption.
- 🌅 **Executive Focus & Morning Briefs**: Every morning at 07:30 AM, Baby LLM reviews your commitments and delivers a concise Morning Readiness Brief, alerting you to overdue milestones.

---

## 🎬 Real-World Workflows in Action

### 1. External Agent in Cursor IDE (FastMCP)
When developing in Cursor or Claude Desktop, your agent calls Baby LLM tools natively:
```text
Agent  > Calling tool: recall_memory(query="Project Phoenix tech stack")
Baby LLM FastMCP >
- [GOAL] user goal_is launch Project Phoenix (Confidence: 95%, Source: hybrid)
- [WORK] user tech_stack FastAPI LanceDB SQLite (Confidence: 100%, Source: bm25)
- [PREFERENCE] user avoids TailwindCSS; prefers Vanilla CSS (Confidence: 90%, Source: vector)

Agent  > Based on your Project Phoenix architecture rules, I will implement the new
         subsystem using FastAPI and Vanilla CSS without external cloud dependencies.

Agent  > Calling tool: commit_fact(subject="project_phoenix", predicate="implements",
                                   object_="fastmcp_stdio_server", category="work")
Baby LLM FastMCP > Successfully committed memory node: project_phoenix implements fastmcp_stdio_server (ID: c7b1a2)
```

### 2. Moving Cities: Bi-Temporal Contradiction Resolution
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

### 3. Medical Allergy & The YMYL Shield
```text
You      > Just left urgent care. Turns out I am severely allergic to penicillin.
Baby LLM > I'm glad you're safe! I have permanently registered your severe penicillin allergy with top priority.

[🌙 REM Dream runs:
   - Category: HEALTH | ymyl_protected: TRUE
   - Encrypted at rest via AES-GCM-256 backed by OS Keyring
   - Ebbinghaus decay curve bypassed: Retention probability R(t) = 1.0 permanently.
]
```

### 4. Direct Human Companion Chat & Gentle Curiosity
```text
You      > Tomorrow I need to finalize the deployment checklist for Project Phoenix.
Baby LLM > Good plan. Ensuring deployment guardrails are locked in will prevent regression bugs.

           💭 By the way, you mentioned Project Phoenix—is this an internal initiative or a client milestone?
```
*(Baby LLM asks at most **one** subtle question per session, never annoying you with constant interrogation).*

### 5. Morning Readiness Brief (07:30 AM)
```text
🌅 Good morning! Here is your Morning Readiness Brief:
• Priority 1: Launch Project Phoenix beta deployment (Due: Today).
• Priority 2: Complete code review for PR #126.
• Alert: Your commitment 'Draft investor update' was due 2 days ago.
• Protect your deep-work window from 09:00 to 12:00.
```

---

## ⚡ High-Level System Architecture

The following diagram illustrates the end-to-end data flow and subsystem topology of Baby LLM:

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

## 📚 Documentation Architecture & File Index

This documentation suite is organized modularly to serve different engineering and user workflows:

| Document | Primary Focus & Coverage | Target Audience |
| :--- | :--- | :--- |
| **[getting-started.md](getting-started.md)** | Agent quickstart, prerequisites, the 5 CLI launch modes, FastMCP configuration for IDEs, and first-run verification. | All Users & Agent Builders |
| **[architecture.md](architecture.md)** | System topology, Tripartite Interaction Architecture, 4-tier memory hierarchy, runtime lifecycles, and concurrency models. | Systems Architects & AI Engineers |
| **[core-engine.md](core-engine.md)** | Sub-30ms fast-path assembler, hybrid RRF retrieval, REM dream consolidation cycle, Ebbinghaus decay math, and persona maturation. | Core Engine Contributors |
| **[configuration-and-storage.md](configuration-and-storage.md)** | Pydantic Settings, environment variables, SQLite WAL/FTS5 schemas, LanceDB tables, AES-GCM-256 encryption, and Obsidian vault sync. | Backend & Database Engineers |
| **[interfaces-and-api.md](interfaces-and-api.md)** | Universal Model Context Protocol (MCP) tools, FastAPI REST specification (Port 21225), CLI commands, and Glass-Box Web UI. | Frontend & Integration Engineers |
| **[development-and-testing.md](development-and-testing.md)** | Local development setup, 39-test pytest execution, mocking strategies, common troubleshooting, and subsystem extension guides. | QA Engineers & Maintainers |

---

## 🧭 Audience-Tailored Reading Paths

Depending on your role and objectives, follow these recommended reading sequences:

### Path A: AI Agent & Tool Integrator 🤖
*Goal: Connect Cursor IDE, Claude Desktop, or autonomous agent frameworks (CrewAI, LangGraph) to Baby LLM as a long-term memory tool.*
1. **[getting-started.md](getting-started.md)**: Follow quickstart steps, launch the FastMCP server, and verify stdio connectivity.
2. **[interfaces-and-api.md](interfaces-and-api.md)**: Deep dive into the Universal Model Context Protocol (MCP) tools (`recall_memory`, `commit_fact`, `get_active_goals`) and the REST API (`/api/memories`).
3. **[architecture.md](architecture.md)**: Study the Tripartite Interaction Architecture and how sub-30ms RRF retrieval prevents agent execution stalling.

### Path B: End User & Local Operator 👤
*Goal: Install Baby LLM, configure local inference, interact via Web UI or Terminal, and manage personal goals.*
1. **[getting-started.md](getting-started.md)**: Install dependencies, configure the virtual environment, and run your first chat session.
2. **[interfaces-and-api.md](interfaces-and-api.md)**: Learn CLI subcommands (`chat`, `serve`, `ui`, `dream`, `memories`) and explore the Glass-Box dashboard.
3. **[configuration-and-storage.md](configuration-and-storage.md)**: Configure environment overrides (`.env`), set custom models or ports, and connect your Obsidian notes vault.

### Path C: Core Systems & AI Engineer 🛠️
*Goal: Understand memory consolidation, hybrid retrieval performance, bi-temporal graph semantics, and mathematical forgetting curves.*
1. **[architecture.md](architecture.md)**: Study the 4-tier biological memory hierarchy, thread concurrency model, and daytime vs. nighttime execution boundaries.
2. **[core-engine.md](core-engine.md)**: Inspect the mathematical formulation of the Ebbinghaus decay curve, the Reciprocal Rank Fusion algorithm, and the bi-temporal conflict resolution logic.
3. **[configuration-and-storage.md](configuration-and-storage.md)**: Review SQLite FTS5 virtual table schemas, synchronization triggers, LanceDB PyArrow definitions, and AES-GCM-256 OS Keyring encryption.
4. **[development-and-testing.md](development-and-testing.md)**: Run the 39-test suite, review unit/integration test gates, and inspect extension points.

---

## 📊 System Feature Matrix

| Subsystem | Underlying Technology | Verified Capabilities & Performance Targets |
| :--- | :--- | :--- |
| **Universal MCP** | FastMCP (`baby-llm-mcp`) | Stdio transport exposing `recall_memory`, `commit_fact`, `get_active_goals`, and `record_daily_win`. |
| **Fast-Path Retrieval** | Reciprocal Rank Fusion (`HybridRetriever`) | <30ms retrieval budget; combines SQLite FTS5 (BM25) and LanceDB dense vectors with $k=60$. |
| **Episodic Buffer** | `EpisodicRingBuffer` (Python `deque`) | Stores last 15 interaction turns in active RAM for immediate conversational continuity. |
| **Full-Text Search** | SQLite FTS5 (`porter unicode61`) | Sub-5ms lexical matching across `subject`, `predicate`, and `object` with automatic trigger synchronization. |
| **Dense Vector Index** | LanceDB + FastEmbed (`bge-small-en-v1.5`) | 384-dimensional dense semantic search using SIMD-accelerated cosine distance; filterable by active state. |
| **Consolidation** | `DreamWorker` (Background Thread) | Monitors 15m idle timeout and 03:00 AM cron; extracts SPO triples; automatically pauses upon user activity. |
| **Conflict Engine** | `ConflictResolver` (Bi-Temporal) | Tracks `valid_from` and `invalid_from`; updates facts without history loss; preserves complete audit trajectories. |
| **Memory Decay** | `EbbinghausDecayEngine` | $R(t) = \exp(-t / (S \cdot I))$; category-weighted importance; infinite retention floor for YMYL health/finance. |
| **Data Encryption** | `YMYLEncryptionManager` (AES-GCM-256) | Attribute-level encryption of sensitive facts at rest; backed by OS Keyring with `0600` local file fallback. |
| **Success Compass** | `PersonalSuccessAgent` + `SuccessTracker` | 07:30 AM Morning Brief with SQLite caching; 21:30 PM Nightly Reflection; accountability watchdog for overdue goals. |
| **Gentle Curiosity** | `GentleCuriosityEngine` | At most 1 subtle clarifying probe per session; detects ambiguous entities (`project <name>`) without annoying users. |
| **Fast-Path Chat** | `ContextAssembler` + `UnifiedLLMProvider` | Sub-30ms assembly overhead; zero-blocking WAL write; automatic fallback from Embedded Qwen to Ollama. |
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
