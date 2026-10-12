# Baby LLM: Implementation Milestones Overview
*A Privacy-First, Self-Evolving Local Memory & Life Success Engine*

---

## 1. System Topology & Architecture

Baby LLM is an autonomous, local-first cognitive companion designed to bridge the gap between stateless local LLMs and long-term personal context. Operating completely offline on consumer hardware with zero cloud dependencies, the system delivers sub-30ms chat path retrieval and delegates fact extraction and memory consolidation to an asynchronous background worker.

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

## 2. Independent Milestones Summary

The full 12-week roadmap is partitioned into four decoupled, independently verifiable milestones:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MILESTONES EXECUTION ROADMAP                          │
├────────────┬──────────────────────────────────┬─────────────┬───────────────┤
│ Milestone  │ Document                         │ Target Span │ Status        │
├────────────┼──────────────────────────────────┼─────────────┼───────────────┤
│ M1         │ MILESTONE_1_FAST_PATH_ENGINE.md  │ Weeks 1 - 3 │ Completed 95% │
│ M2         │ MILESTONE_2_REM_DREAM_ENGINE.md  │ Weeks 4 - 6 │ Completed 85% │
│ M3         │ MILESTONE_3_MCP_SERVER_AND_UI.md │ Weeks 7 - 9 │ Completed 80% │
│ M4         │ MILESTONE_4_SUCCESS_AND_SYNC.md  │ Weeks 10-12 │ Partial   50% │
└────────────┴──────────────────────────────────┴─────────────┴───────────────┘
```

### [Milestone 1: Fast-Path Engine & WAL Store](file:///Users/admin/Desktop/corporate/projects/baby-llm/implementation/milestones/MILESTONE_1_FAST_PATH_ENGINE.md)
* **Objective**: Zero-lag (< 30ms overhead) synchronous chat interaction path with instant SQLite WAL appending and sub-20ms hybrid retrieval.
* **Key Components**: SQLite WAL connection manager, LanceDB vector storage, FastEmbed BGE-Small ONNX embedder, FTS5 BM25 search, Reciprocal Rank Fusion (RRF), episodic ring buffer, and embedded Qwen2.5-0.5B inference engine.
* **Primary Gate**: **G1** (Context retrieval + assembly < 30ms).

### [Milestone 2: The REM Dream Engine & Bi-Temporal Graph](file:///Users/admin/Desktop/corporate/projects/baby-llm/implementation/milestones/MILESTONE_2_REM_DREAM_ENGINE.md)
* **Objective**: Offline background cognitive consolidation extracting atomic Subject-Predicate-Object (SPO) facts, resolving temporal contradictions, and computing scientific Ebbinghaus memory decay.
* **Key Components**: Quantized SLM triple extraction pipeline, bi-temporal graph store (`valid_from` / `invalid_from`), Ebbinghaus mathematical decay engine with YMYL immunity shield, and consolidation cycle coordinator.
* **Primary Gates**: **G2** (> 95% contradiction accuracy), **G3** (Ebbinghaus curve adherence), **G4** (100% YMYL immunity), **G5** (< 1.0GB memory ceiling).

### [Milestone 3: Universal MCP Server & Glass-Box Dashboard](file:///Users/admin/Desktop/corporate/projects/baby-llm/implementation/milestones/MILESTONE_3_MCP_SERVER_AND_GLASS_BOX_UI.md)
* **Objective**: Transparent glass-box inspectability and ecosystem connectivity via Model Context Protocol (MCP) and dedicated collision-proof port 21225 web dashboard.
* **Key Components**: Universal MCP Server (stdio transport for Claude Desktop / Cursor / Zed), FastAPI local REST bridge on port 21225 (`BABY`), Mindstream card feed, Bi-temporal visual timeline, and one-click fact erase/override.
* **Primary Gate**: **G6** (Seamless MCP client interoperability).

### [Milestone 4: Proactive Success Agent & Local Ecosystem Sync](file:///Users/admin/Desktop/corporate/projects/baby-llm/implementation/milestones/MILESTONE_4_SUCCESS_AGENT_AND_ECOSYSTEM_SYNC.md)
* **Objective**: Transformation into an active success companion with scheduled morning/evening routines, gentle curiosity, bidirectional Obsidian markdown synchronization, and OS keyring encryption.
* **Key Components**: Personal Success Agent (Morning Brief 07:30, Nightly Reflection 21:30, Accountability Watchdog), Gentle Curiosity engine, Watchdog bidirectional markdown sync, AES-GCM-256 YMYL encryption, and CLI launcher suite.
* **Primary Gate**: **G7** (Air-gapped privacy with 0 outbound cloud requests).

---

## 3. Inter-Milestone Dependency Matrix

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DATA FLOW & DEPENDENCY RELATIONSHIPS                    │
└─────────────────────────────────────────────────────────────────────────────┘

  [Milestone 1: Fast-Path & WAL]
        │
        │ Writes raw turns to interaction_log
        ▼
  [Milestone 2: REM Dream Consolidation]
        │
        │ Extracts SPO triples & updates active nodes
        ▼
  [Milestone 3: MCP Server & Glass-Box UI]
        │
        │ Exposes verified facts & allows user audits/edits
        ▼
  [Milestone 4: Success Loops & Obsidian Vault Sync]
        │
        └─► Bidirectional sync with local Markdown files & scheduled briefs
```

---

## 4. Verification Gates Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VERIFICATION GATES                                 │
├────┬─────────────────────────────┬───────────────────────────┬──────────────┤
│ #  │ Verification Gate           │ Validation Metric         │ Status       │
├────┼─────────────────────────────┼───────────────────────────┼──────────────┤
│ G1 │ Fast-Path Latency Overhead  │ Assembly overhead < 30ms  │ Verified     │
│ G2 │ Contradiction Accuracy      │ > 95% on conflict suite   │ Verified     │
│ G3 │ Memory Decay Mathematics    │ Strict Ebbinghaus curves  │ Verified     │
│ G4 │ YMYL Category Immunity      │ 100% retention floor      │ Verified     │
│ G5 │ Background Resource Ceiling │ SLM memory < 1.0GB RAM    │ Verified     │
│ G6 │ MCP Client Compatibility    │ Cursor & Claude interoper │ Partial      │
│ G7 │ Air-Gapped Privacy          │ 0 outbound cloud requests │ Verified     │
└────┴─────────────────────────────┴───────────────────────────┴──────────────┘
```
