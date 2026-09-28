# Baby LLM: Product Blueprint & Architectural Specification
*The Privacy-First, Self-Evolving Local Memory & Life Companion Engine*

---

## 1. Executive Summary & Product Vision

### 1.1 Why "Baby LLM"?
Current local AI frameworks treat Large Language Models as cold, stateless compute engines with vector databases bolted onto their sides. When memory frameworks are added, they are either:
1. **Academic/Brittle Python scripts** (like `widemem-ai`), which freeze the chat interface by running synchronous multi-shot LLM evaluations on every interaction.
2. **Heavyweight enterprise microservices** (like `Memobase` or `Zep`), which require complex Docker stacks, cloud API credits, and lack consumer privacy safeguards.
3. **Developer-only abstraction libraries** (like `Mem0`, `Cognee`, or `LangMem`), which lack an intuitive, human-centered desktop companion experience.

**Baby LLM** is born from a radically human concept: **An AI companion that starts as an infant (high curiosity, clean slate, zero bias) and organically matures into an indispensable personal confidant and life success manager.**

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BABY LLM MATURITY CONTINUUM                         │
├─────────────────┬──────────────────┬───────────────────┬────────────────────┤
│  1. INFANCY     │  2. TODDLER      │  3. APPRENTICE    │  4. DIGITAL TWIN   │
│  (Days 1 - 7)   │  (Weeks 2 - 4)   │  (Months 2 - 6)   │  (Year 1+)         │
├─────────────────┼──────────────────┼───────────────────┼────────────────────┤
│ • High Curiosity│ • Recognizes     │ • Antici-         │ • High-fidelity    │
│ • Gentle probing│   patterns &     │   pates needs &   │   cognitive sync   │
│   questions     │   routines       │   deadlines       │ • Proactive        │
│ • Builds baseline│• Maps key       │ • Flags personal  │   advisory &       │
│   identity graph│   relationships  │   contradictions  │   strategic counsel│
│ • Learns user   │ • Calibrates     │ • Proactive goal  │ • Lifelong memory  │
│   tone & voice  │   response style │   coaching        │   anchor           │
└─────────────────┴──────────────────┴───────────────────┴────────────────────┘
```

### 1.2 Core Mission: Solving the Modern Cognitive Deficit
Baby LLM is engineered to solve four foundational problems of modern knowledge workers and everyday individuals:
* **Overwhelmed Focus**: Thoughts, commitments, medical notes, and goals vanish into fragmented note apps.
* **Fear of Cloud Surveillance**: People will never share their deepest financial anxieties, health symptoms, or confidential career plans with cloud APIs that log or train on private inputs.
* **Context Amnesia**: Every time a user opens a new chat session with typical tools, they start from zero.
* **Passive Inertia**: Traditional chatbots wait passively to be queried instead of proactively keeping the user accountable to their own aspirations.

---

## 2. Competitive Intelligence & SOTA Framework Teardown

To build a world-class engine, Baby LLM synthesizes the strengths and eliminates the fatal flaws of all major existing memory frameworks:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            SOTA MEMORY FRAMEWORK BENCHMARK MATRIX                                │
├───────────────┬──────────────────────┬─────────────┬────────────────┬──────────────┬─────────────┤
│ Framework     │ Architecture / Type  │ Offline/    │ Memory Model   │ Conflict /   │ Primary     │
│               │                      │ Self-Hosted │ & Storage      │ Time Engine  │ Weakness    │
├───────────────┼──────────────────────┼─────────────┼────────────────┼──────────────┼─────────────┤
│ Mem0          │ Library & Cloud API  │ Partial     │ Vector +       │ Dynamic fact │ Heavy cloud │
│ (SOTA Drop-in)│ (Python / TS)        │ (Docker/OSS)│ Graph store    │ overwrite /  │ bias; sync  │
│               │                      │             │ (Qdrant/Neo4j) │ deduplication│ latency tax │
├───────────────┼──────────────────────┼─────────────┼────────────────┼──────────────┼─────────────┤
│ Graphiti      │ Open-Source Engine   │ Full OSS    │ Temporal       │ Temporal     │ Complex Neo4j│
│ (Zep Engine)  │ (Python client / API)│ (Self-host) │ Knowledge Graph│ validity edges│ setup; heavy│
│               │                      │             │ (Neo4j/Kuzu)   │ (valid_until)│ for edge CPU│
├───────────────┼──────────────────────┼─────────────┼────────────────┼──────────────┼─────────────┤
│ Letta         │ Agentic Memory Server│ Full OSS    │ OS Paging      │ Manual agent │ High token  │
│ (ex-MemGPT)   │ (Python / Docker)    │ (Ollama)    │ (Core, Recall, │ function calls│ consumption;│
│               │                      │             │ Archival/PG)   │ to edit tags │ complex API │
├───────────────┼──────────────────────┼─────────────┼────────────────┼──────────────┼─────────────┤
│ Cognee        │ Data pipeline &      │ Full OSS    │ Graph-first    │ Entity node  │ Requires pipeline│
│               │ memory engine        │ (Local DBs) │ + Vector index │ clustering & │ orchestration│
│               │                      │             │ (LanceDB/Duck) │ graph schema │ (not drop-in)│
├───────────────┼──────────────────────┼─────────────┼────────────────┼──────────────┼─────────────┤
│ Khoj          │ Full Desktop / Web   │ 100% Local  │ Document RAG   │ File sync &  │ Doc-focused;│
│               │ Personal Assistant   │ (Ollama/Py) │ (LanceDB/PG)   │ semantic re- │ lacks atomic │
│               │                      │             │                │ indexing     │ user traits │
├───────────────┼──────────────────────┼─────────────┼────────────────┼──────────────┼─────────────┤
│ widemem-ai    │ Local-first Python   │ 100% Local  │ Hierarchical   │ Regex + LLM  │ Brittle regex│
│               │ library              │ (SQLite/    │ (Facts, Themes)│ check; linear│ checks; synchronous│
│               │                      │  FAISS)     │                │ time-decay   │ chat freezes │
├───────────────┼──────────────────────┼─────────────┼────────────────┼──────────────┼─────────────┤
│ Memobase      │ Memory Microservice  │ Self-host / │ Continuous     │ Interaction  │ Microservice │
│               │ (REST API server)    │ Docker      │ User Profile   │ batch-buffer │ ops overhead;│
│               │                      │             │ Synthesis      │ queue        │ lacks decay  │
├───────────────┼──────────────────────┼─────────────┼────────────────┼──────────────┼─────────────┤
│ BABY LLM      │ Native Desktop +     │ 100% Local  │ Bi-Temporal    │ Asynchronous │ None of the │
│ (Our Product) │ Embedded MCP Server  │ Zero-Cloud  │ Graph + Hybrid │ REM Dream    │ above: 0-lag│
│               │ (Tauri + Rust/Python)│ Sovereign   │ LanceDB/SQLite │ Consolidation│ & glass-box │
└───────────────┴──────────────────────┴─────────────┴────────────────┴──────────────┴─────────────┘
```

### Architectural Synthesis: What Baby LLM Adopts & Elevates
1. **From Graphiti (Zep)**: **Bi-Temporal Validity Windows** (`valid_from`, `invalid_from`). When a user updates a fact (*"I lived in Austin"* $\to$ *"I moved to Seattle"*), Austin is not deleted; its validity window is closed, preserving chronological history. We implement this natively in **SQLite** rather than requiring a heavyweight Neo4j cluster.
2. **From widemem-ai**: **YMYL (Your Money or Your Life) Immunity**. Financial obligations, health conditions, allergies, and core values are assigned infinite retention and immunity from forgetting.
3. **From Memobase**: **Asynchronous Write-Ahead Buffering**. Conversations write instantly to a zero-overhead local append log; heavy extraction never freezes the chat UI.
4. **From Letta (MemGPT)**: **Tiered Context Paging**, but with automatic edge heuristics instead of expensive LLM tool-calling loops.
5. **From Khoj**: **Local File & Markdown Vault Interoperability** (bidirectional sync with Obsidian and plain text).

---

## 3. The 4-Tier Biological Memory Hierarchy

Baby LLM organizes memory across four cognitive tiers, mirroring human neurological processing:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BABY LLM 4-TIER MEMORY HIERARCHY                       │
├─────────────────┬───────────────────────────────┬───────────────────────────┤
│ Tier            │ Storage & Mechanism           │ Cognitive Function        │
├─────────────────┼───────────────────────────────┼───────────────────────────┤
│ 1. Sensory &    │ In-memory ring buffer +       │ Immediate conversation    │
│    Episodic     │ SQLite Write-Ahead Log (WAL)  │ continuity (last 10-15    │
│    Buffer       │                               │ turns + audio transcripts)│
├─────────────────┼───────────────────────────────┼───────────────────────────┤
│ 2. Bi-Temporal  │ SQLite relational graph +     │ Evolving factual knowledge│
│    Knowledge    │ LanceDB vector embeddings     │ with historical timestamps│
│    Graph        │ (HNSW index)                  │ (entities, preferences)   │
├─────────────────┼───────────────────────────────┼───────────────────────────┤
│ 3. Persona &    │ AES-GCM-256 encrypted local   │ Deep psychological traits,│
│    YMYL Vault   │ store + Markdown front-matter │ communication style,      │
│                 │                               │ allergies, values, finances│
├─────────────────┼───────────────────────────────┼───────────────────────────┤
│ 4. Personal     │ State-machine tracker in      │ Active commitments, daily │
│    Success      │ DuckDB / SQLite               │ habits, accountability,   │
│    Engine       │                               │ energy cycles, milestones │
└─────────────────┴───────────────────────────────┴───────────────────────────┘
```

---

## 4. System Architecture & The "REM Dream" Engine

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BABY LLM SYSTEM ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────┘

       ┌───────────────────────────────────────────────────────────────┐
       │                       CLIENT APPLICATIONS                     │
       │  • Baby LLM Native Desktop (Tauri)   • Mobile Companion (PWA) │
       │  • Claude Desktop / Cursor (via MCP) • Raycast / CLI Widget   │
       └───────────────────────────────┬───────────────────────────────┘
                                       │
                         User Prompt   │ Real-time Stream (< 30ms latency overhead)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. DAYTIME FAST-PATH (Real-Time Zero-Lag Cognition)                         │
│                                                                             │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │ Working Context Assembler                                            │  │
│   │   • Last 10 Episodic Turns                                           │  │
│   │   • Active Persona Core & Current Success Directives                 │  │
│   │   • Sub-20ms Hybrid Retrieval:                                       │  │
│   │       - BM25 Full-Text Search (Exact entities, names, codes)         │  │
│   │       - LanceDB Local Vector Search (Semantic nuance)                │  │
│   └───────────────────────────────────┬──────────────────────────────────┘  │
│                                       │                                      │
│                                       ▼                                      │
│                       Local LLM (Ollama / llama.cpp)                         │
│                       (e.g., Llama 3.2 3B, Qwen 2.5 7B, Mistral Nemo)        │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        │ Appends raw turn instantaneously to
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. WRITE-AHEAD INTERACTION LOG (WAL - SQLite Embedded)                      │
│    • Timestamps • Raw Turns • Sentiment Tags • Extracted Task Triggers      │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        │ Triggers on System Idle / Night Timer
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. THE "REM DREAM" CONSOLIDATION ENGINE (Background Autonomous Worker)      │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Local Quantized SLM Worker (SmolLM2-1.7B-Q4 / Qwen2.5-1.5B-Q4)      │   │
│   │                                                                     │   │
│   │  [Fact Extraction] ──▶ [Temporal Graph Update] ──▶ [Decay Compute]  │   │
│   │           │                       │                      │          │   │
│   │           ▼                       ▼                      ▼          │   │
│   │    Subject-Predicate-      valid_from/invalid_to     Ebbinghaus     │   │
│   │    Object Triples          Timeline Anchoring        Retention Curve│   │
│   │                                                      (YMYL Immune)  │   │
│   └───────────────────────────────────┬─────────────────────────────────┘   │
│                                       │                                      │
│                                       ▼                                      │
│           Bi-Temporal Graph & Vector Re-index (SQLite + LanceDB)            │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. "GLASS-BOX" VAULT & LIFE SUCCESS COMPASS                                 │
│    • Visual Memory Stream  • One-Click Node Erase  • Accountability Matrix  │
│    • Markdown / Obsidian Vault Sync • Local Backup & Restore                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Breakthrough Technical Mechanisms

### 5.1 Bi-Temporal Graphiti-Style Fact Engine in SQLite
Rather than running an external graph database, Baby LLM uses a hyper-optimized relational graph schema directly inside embedded SQLite:

```sql
-- Core Memory Node
CREATE TABLE memory_nodes (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    category TEXT CHECK(category IN ('lifestyle', 'health', 'finance', 'work', 'relationship', 'goal')),
    confidence REAL DEFAULT 1.0,
    valid_from TIMESTAMP NOT NULL,
    invalid_from TIMESTAMP,         -- NULL means currently valid
    ymyl_protected BOOLEAN DEFAULT 0,
    source_turn_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Temporal Query: "What is currently true about the user's career?"
SELECT * FROM memory_nodes 
WHERE subject = 'user' 
  AND category = 'work' 
  AND invalid_from IS NULL;

-- Historical Query: "What was the user's role before their current promotion?"
SELECT * FROM memory_nodes 
WHERE subject = 'user' 
  AND predicate = 'works_as' 
  AND invalid_from IS NOT NULL 
ORDER BY invalid_from DESC LIMIT 1;
```

### 5.2 The "REM Dream" Consolidation Pipeline
When the user's machine is idle for > 15 minutes, or at a configured hour (e.g., 3:00 AM), Baby LLM spins up a background thread running a sub-2B SLM (e.g. `SmolLM2-1.7B` taking only ~800 MB of VRAM).

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       REM DREAM CONSOLIDATION STEPS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ STEP 1: INGESTION                                                           │
│ Read all unindexed interaction logs from SQLite WAL since last dream cycle. │
├─────────────────────────────────────────────────────────────────────────────┤
│ STEP 2: ATOMIC EXTRACTION                                                   │
│ Extract atomic facts into (Subject, Predicate, Object) triplets with        │
│ confidence scores and category labels.                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ STEP 3: CONTRADICTION & TEMPORAL RESOLUTION                                 │
│ If a new fact contradicts an existing active fact:                          │
│ • Set the existing node's `invalid_from` = current_timestamp.               │
│ • Insert the new node with `valid_from` = current_timestamp.                │
├─────────────────────────────────────────────────────────────────────────────┤
│ STEP 4: EBBINGHAUS DECAY & PRUNING                                          │
│ Recompute retention score R(t) = exp(-t / (S * I)).                         │
│ • If YMYL_protected == TRUE: Skip decay entirely.                           │
│ • If R(t) < 0.20: Archive node from working vector store to cold disk.      │
├─────────────────────────────────────────────────────────────────────────────┤
│ STEP 5: DAILY SYNTHESIS GENERATION                                          │
│ Synthesize a 3-bullet "Morning Readiness Brief" for the user's next login.  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Scientific Ebbinghaus Forgetting Curve with YMYL Shield
```text
      Retention %
        100% ┼───────────────────────── YMYL Protected (Health, Finance, Values)
             │ \
             │  \                      Without review (Trivia: "User bought coffee")
             │   \
             │    ─────                With 1 review / reinforcement
             │         ───────
          0% ┼───────────────────────
             0d    2d    7d    30d     Time (Days)
```
* Every time the user mentions or references an existing fact, the stability factor $S$ doubles ($S_{new} = S_{old} \times 2$), mimicking human spaced repetition.
* Trivial episodic banter fades out cleanly over 14 days, preventing vector database bloat.
* Critical facts flagged with `ymyl_protected = 1` have an infinite retention floor.

---

## 6. Personal Success & Proactive Coaching Engine

Baby LLM moves beyond passive memory into **active partnership**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE PERSONAL SUCCESS AGENTIC LOOP                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. The Morning Intention Brief (07:30 AM)                                   │
│    • Yesterday's open loops & resolved decisions.                           │
│    • Top 2 needle-moving priorities based on long-term strategy.            │
│    • Energy pacing recommendation based on meeting calendar density.        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. The Gentle Curiosity Protocol (During Conversation)                      │
│    • When Baby LLM detects an undefined entity or ambiguous priority,       │
│      it asks at most ONE gentle clarifying question per session.            │
│      (e.g., "You mentioned 'Project Titan' twice—is this a client or internal?")│
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. The Accountability Watchdog                                              │
│    • Detects dropped commitments: "On Monday you wanted to finish the pitch │
│      deck by Thursday. It's Friday morning—do you need a focus block?"      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. The Nightly Reflection & Unload (09:30 PM)                               │
│    • Frictionless "Brain Dump" space.                                       │
│    • Flags wins and acknowledges friction points to clear mental runway.    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Interactive "Glass-Box" UI Specification

Unlike opaque enterprise memory systems, Baby LLM provides a visual, native dashboard:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ BABY LLM DASHBOARD                      [Status: Awake] [VRAM: 1.2GB] [🔒AES]│
├───────────────────────────────────┬─────────────────────────────────────────┤
│ 🧠 MINDSTREAM (Recent Learnings)  │ 🎯 SUCCESS COMPASS                      │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ [Health] Fasting window: 8pm-12pm │ Active Goal: Launch MVP by Oct 15       │
│ Confidence: 96%  [Edit] [Forget]  │ Progress: [████████░░░░] 65%            │
│                                   │ Next Milestone: Complete LanceDB sync   │
│ [Work] Leading Project Titan      │                                         │
│ Confidence: 92%  [Edit] [Forget]  ├─────────────────────────────────────────┤
│                                   │ 📅 COMMITMENT LOOP                      │
│ [Preference] Prefers bullet points│ • [ ] Send investor update (Overdue 1d) │
│ Confidence: 88%  [Edit] [Forget]  │ • [X] Draft system architecture blueprint│
├───────────────────────────────────┴─────────────────────────────────────────┤
│ 🕸️ BI-TEMPORAL TIMELINE INSPECTOR                                           │
│ [2024-03-01 ──▶ 2025-08-15] Lived in Seattle (Archived)                    │
│ [2025-08-16 ──▶ Present   ] Living in Austin, Texas (Active Node)           │
├─────────────────────────────────────────────────────────────────────────────┤
│ [➕ Add Memory]  [👁️ Incognito Mode]  [📥 Export Markdown]  [⚙️ Settings]    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Open-Source Extensibility & Ecosystem Integration

### 8.1 Universal Model Context Protocol (MCP) Server
Baby LLM runs a local MCP server (`baby-llm-mcp`). Any MCP-compatible tool can attach to Baby LLM's unified memory:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BABY LLM UNIVERSAL MCP TOPOLOGY                        │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │ Claude Desktop  │    │   Cursor IDE    │    │ Terminal / CLI  │
    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │ stdio / SSE
                                    ▼
                 ┌──────────────────────────────────────┐
                 │          BABY LLM MCP SERVER         │
                 │ Tools:                               │
                 │  • `recall_memory(query, scope)`     │
                 │  • `commit_fact(subject, predicate)` │
                 │  • `get_active_goals()`              │
                 │  • `record_daily_win(note)`          │
                 └──────────────────┬───────────────────┘
                                    │
                                    ▼
                 ┌──────────────────────────────────────┐
                 │       LOCAL ENCRYPTED VAULT          │
                 │      (SQLite + LanceDB Disk)         │
                 └──────────────────────────────────────┘
```
* **Benefit**: Your AI memory is no longer trapped in a single app. When you switch between coding in Cursor, writing in Claude Desktop, and chatting in the Baby LLM UI, your personal context is unified.

### 8.2 Markdown & Obsidian Bidirectional Local Sync
* Every verified memory node can be exported or mirrored to a local folder: `~/BabyLLM/vault/`.
* You can edit your facts in Obsidian using standard Markdown front-matter; Baby LLM re-indexes them instantly via local file watchers.

---

## 9. Technology Stack & Deployment Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRODUCTION TECH STACK                             │
├───────────────────┬───────────────────────────────┬─────────────────────────┤
│ Component         │ Chosen Technology             │ Technical Rationale     │
├───────────────────┼───────────────────────────────┼─────────────────────────┤
│ Desktop Shell     │ Tauri v2 (Rust + Webview)     │ Binary < 15MB, RAM < 35MB│
│ Backend Service   │ Python 3.11+ (FastAPI/Rust)   │ Native AI ecosystem     │
│ Local Vector DB   │ LanceDB (disk-native columnar)│ Zero-daemon, blazing    │
│                   │                               │ SIMD vector queries     │
├───────────────────┼───────────────────────────────┼─────────────────────────┤
│ Relational Graph  │ SQLite (WAL mode, foreign keys│ Serverless, ACID,       │
│ & Write-Ahead Log │ enabled, json1 extension)     │ zero-ops persistence    │
├───────────────────┼───────────────────────────────┼─────────────────────────┤
│ Local Chat LLM    │ Ollama / llama.cpp (GGUF)     │ Metal/CUDA acceleration │
│ Dream SLM         │ SmolLM2-1.7B / Qwen2.5-1.5B   │ Consumes < 800MB VRAM   │
├───────────────────┼───────────────────────────────┼─────────────────────────┤
│ Local Embeddings  │ BAAI/bge-small-en-v1.5 (ONNX) │ 384-dim, 1500 tokens/sec│
│ Security Layer    │ AES-GCM-256 via OS Keyring    │ Complete data protection│
└───────────────────┴───────────────────────────────┴─────────────────────────┘
```

---

## 10. Implementation Phasing & Development Roadmap

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BABY LLM EXECUTION PHASING                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 1: THE INFANT ENGINE (Weeks 1 - 3)                                    │
│ • Implement SQLite WAL logger & LanceDB hybrid retriever.                   │
│ • Build the Ollama local chat bridge (zero-lag prompt assembly).            │
│ • Create basic command-line chat testing episodic continuity.               │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 2: THE DREAM CYCLE & BI-TEMPORAL GRAPH (Weeks 4 - 6)                  │
│ • Asynchronous REM worker triggering on system idle.                        │
│ • Fact extraction prompt pipeline using a local sub-2B SLM.                 │
│ • Implement `valid_from` / `invalid_from` temporal resolution logic.        │
│ • Add Ebbinghaus forgetting curve math and YMYL immunity flags.             │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 3: THE GLASS-BOX DASHBOARD & MCP SERVER (Weeks 7 - 9)                 │
│ • Build the Tauri desktop app and local web control panel.                  │
│ • Implement visual memory cards with edit, pin, and erase capabilities.     │
│ • Expose standard Model Context Protocol (MCP) server endpoints.            │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 4: PERSONAL SUCCESS AGENT & OPEN-SOURCE LAUNCH (Weeks 10 - 12)        │
│ • Morning Intention Briefing & Nightly Reflection loops.                    │
│ • Bidirectional Obsidian vault synchronization.                             │
│ • Publish open-source repository under Apache 2.0 / MIT license.            │
└─────────────────────────────────────────────────────────────────────────────┘
```
