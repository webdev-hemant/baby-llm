# Milestone 1: Fast-Path Engine & WAL Store
*Weeks 1 – 3 • Primary Objective: Sub-30ms Synchronous Interaction & Retrieval Pipeline*

---

## 1. Executive Summary & Objective

The primary objective of **Milestone 1** is to establish a zero-lag (< 30ms overhead) real-time interaction loop. When a user sends a message, Baby LLM must:
1. Instantly retrieve relevant active memories and open commitments without blocking the chat path.
2. Assemble a concise, developmental-stage prompt incorporating the user's episodic conversation turns.
3. Stream or generate responses using a local, zero-daemon quantized SLM ([`EmbeddedLLMEngine`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/runtime/embedded_engine.py#L17) running `Qwen2.5-0.5B-Instruct-GGUF`), with optional fallback to Ollama.
4. Atomically append the conversation turn to an embedded SQLite Write-Ahead Log ([`WriteAheadLog`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/storage/wal.py#L8)) for later asynchronous background processing.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MILESTONE 1 RUNTIME ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────────────┘

  User Message ──► Context Assembler (< 20ms) ────────► Embedded Qwen2.5-0.5B
                        │                                      │
                        ├─► Ring Buffer (15 turns)             ▼
                        ├─► SQLite FTS5 (BM25 exact)     Instant Reply (<30ms)
                        ├─► LanceDB (BGE Vector dense)         │
                        └─► Active Commitments                 ▼
                                                      Append to SQLite WAL
                                                      (interaction_log)
```

---

## 2. Component Layout & Module Map

| Module Path | Primary Symbols / Classes | Responsibility |
| :--- | :--- | :--- |
| [`src/baby_llm/config.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/config.py) | [`Settings`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/config.py#L8) | Manages `~/.baby_llm/` paths, port `21225`, and thresholds |
| [`src/baby_llm/core/models.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/core/models.py) | [`InteractionTurn`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/core/models.py#L25), [`MemoryNode`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/core/models.py#L36) | Pydantic data models and schemas |
| [`src/baby_llm/core/ring_buffer.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/core/ring_buffer.py) | [`EpisodicRingBuffer`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/core/ring_buffer.py#L7) | In-memory 15-turn FIFO episodic cache |
| [`src/baby_llm/storage/db.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/storage/db.py) | [`DatabaseManager`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/storage/db.py#L92) | SQLite connection pool (`PRAGMA journal_mode = WAL`) |
| [`src/baby_llm/storage/wal.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/storage/wal.py) | [`WriteAheadLog`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/storage/wal.py#L8) | Appends raw dialogue turns in sub-millisecond writes |
| [`src/baby_llm/storage/vector_store.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/storage/vector_store.py) | [`LanceVectorStore`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/storage/vector_store.py#L11) | LanceDB disk-native dense vector storage |
| [`src/baby_llm/retrieval/embedder.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/retrieval/embedder.py) | [`LocalEmbedder`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/retrieval/embedder.py#L9) | FastEmbed BAAI/bge-small-en-v1.5 ONNX runtime |
| [`src/baby_llm/retrieval/bm25.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/retrieval/bm25.py) | [`BM25Retriever`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/retrieval/bm25.py#L7) | SQLite FTS5 keyword BM25 retrieval |
| [`src/baby_llm/retrieval/hybrid.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/retrieval/hybrid.py) | [`HybridRetriever`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/retrieval/hybrid.py#L12) | Reciprocal Rank Fusion ($k=60$) rank merge |
| [`src/baby_llm/runtime/context_assembler.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/runtime/context_assembler.py) | [`ContextAssembler`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/runtime/context_assembler.py#L17) | Compiles system persona, memories, buffer turns |
| [`src/baby_llm/runtime/embedded_engine.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/runtime/embedded_engine.py) | [`EmbeddedLLMEngine`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/runtime/embedded_engine.py#L17) | Thread-safe embedded GGUF llama-cpp-python engine |
| [`src/baby_llm/runtime/llm_provider.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/runtime/llm_provider.py) | [`UnifiedLLMProvider`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/runtime/llm_provider.py#L11) | Primary embedded SLM with fallback to Ollama |
| [`src/baby_llm/cli.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/cli.py) | [`interactive_chat()`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/cli.py#L15) | Terminal interactive chat interface |

---

## 3. Storage Schema & Mathematical Formulations

### 3.1 SQLite WAL Interaction Log
```sql
CREATE TABLE IF NOT EXISTS interaction_log (
    turn_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_input TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    sentiment_tag TEXT,
    processed_in_dream BOOLEAN DEFAULT 0
);
```

### 3.2 LanceDB Vector Schema
```text
Table: "memories"
├── id: string (UUID)
├── vector: list<float32>[384]
├── text: string (Human-readable fact)
├── category: string
├── is_active: bool
└── ymyl_protected: bool
```

### 3.3 Reciprocal Rank Fusion (RRF) Retrieval Formula
Exact entity keywords and conceptual queries are unified using Reciprocal Rank Fusion:

$$RRF\_Score(d) = \sum_{m \in \{bm25, vector\}} \frac{1}{60 + rank_m(d)}$$

Where:
* $rank_{bm25}(d)$ is the position of document $d$ in the SQLite FTS5 rank order.
* $rank_{vector}(d)$ is the position of document $d$ in the LanceDB cosine similarity order.
* Constant $k = 60$ prevents top-ranked individual matches from skewing overall relevance.

---

## 4. Implementation Tasks & Deliverables

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MILESTONE 1 IMPLEMENTATION CHECKLIST                    │
├──────┬─────────────────────────────────────────────────┬────────────────────┤
│ Item │ Task Description                                │ Verification       │
├──────┼─────────────────────────────────────────────────┼────────────────────┤
│ 1.1  │ Scaffold project layout & config settings       │ Path creation unit │
│ 1.2  │ SQLite connection manager with WAL mode         │ Test WAL pragma    │
│ 1.3  │ Sub-millisecond WAL turn appender               │ test_wal.py        │
│ 1.4  │ FastEmbed ONNX 384-dim embedder                 │ Embedder fixture   │
│ 1.5  │ LanceDB disk-native vector indexer              │ Table CRUD test    │
│ 1.6  │ SQLite FTS5 virtual table with porter tokenizer │ Match query test   │
│ 1.7  │ Reciprocal Rank Fusion (RRF) ranker             │ test_hybrid.py     │
│ 1.8  │ Fast-path Context Assembler (< 20ms)            │ Benchmark fixture  │
│ 1.9  │ Embedded Qwen2.5-0.5B inference engine          │ llama-cpp chat     │
└──────┴─────────────────────────────────────────────────┴────────────────────┘
```

---

## 5. Verification Gates & Automated Test Suites

### 5.1 Verification Gates
* **Gate G1 (Fast-Path Latency Overhead)**: Total overhead of context retrieval and assembly must remain strictly under 30ms.
* **Gate G7 (Air-Gapped Privacy)**: 0 outbound external network connections initiated during dialogue flow.

### 5.2 Test Coverage
* [`tests/unit/test_wal.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/unit/test_wal.py):
  * `test_append_and_retrieve_unprocessed_turns()`: Verifies persistent turn storage.
  * `test_mark_turns_processed()`: Verifies dream consumption tracking.
* [`tests/unit/test_hybrid_retrieval.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/unit/test_hybrid_retrieval.py):
  * `test_hybrid_retrieval_rrf()`: Verifies that unified rankings incorporate both keyword and semantic hits.

---

## 6. Current Implementation Status & Outstanding Work

* **Completed (100%)**:
  * SQLite WAL storage, LanceDB, FastEmbed ONNX, FTS5 BM25, and RRF hybrid retrieval are completely implemented and passing tests.
  * Context Assembler and embedded Qwen2.5-0.5B inference engine operate self-contained inside Python.
  * Runtime dependencies (`llama-cpp-python`, `huggingface-hub`, `pyyaml`) added to [`pyproject.toml`](file:///Users/admin/Desktop/corporate/projects/baby-llm/pyproject.toml).
  * Unit test suite ([`tests/unit/test_wal.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/unit/test_wal.py), [`tests/unit/test_hybrid_retrieval.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/unit/test_hybrid_retrieval.py)) fully updated, verified, and passing (16/16 tests passing across test suite).
* **Remaining Action Items**:
  * None. Milestone 1 is 100% complete, verified, and ready for Milestone 2 REM Dream engine ingestion.
