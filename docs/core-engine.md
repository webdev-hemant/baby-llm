# 🧠 Core Engine: Fast-Path Assembly, Dream Consolidation & Persona Maturation

*Sub-30ms Context Assembler, Hybrid RRF Retrieval, Asynchronous Consolidation, Ebbinghaus Decay Mathematics, and Persona Evolution*

---

## 1. Fast-Path Context Assembler (`ContextAssembler`)

The **Fast-Path Context Assembler** (`src/baby_llm/runtime/context_assembler.py`) and **Hybrid Retrieval Engine** (`src/baby_llm/retrieval/hybrid.py`) provide the real-time runtime engine responsible for synthesizing prompt payloads and serving external agent memory queries (`recall_memory`) under a strict **sub-30ms latency budget**.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   SUB-30MS LATENCY BUDGET BREAKDOWN                    │
├───────────────────────────────────┬────────────────────────────────────┤
│ Pipeline Stage                    │ Target Latency Overhead            │
├───────────────────────────────────┼────────────────────────────────────┤
│ 1. BM25 FTS5 Lexical Search       │ 1.5 – 3.0 ms                       │
│ 2. FastEmbed Dense Vector Search  │ 8.0 – 12.0 ms                      │
│ 3. Reciprocal Rank Fusion (RRF)   │ 0.5 – 1.0 ms                       │
│ 4. Active Commitments Query       │ 0.8 – 1.5 ms                       │
│ 5. Working Prompt Compilation     │ 0.2 – 0.5 ms                       │
├───────────────────────────────────┼────────────────────────────────────┤
│ TOTAL CONTEXT ASSEMBLY OVERHEAD   │ < 18.0 ms (Well under 30ms limit)  │
└───────────────────────────────────┴────────────────────────────────────┘
```

### 1.1 Base Persona Injection
Every interaction prompt is seeded with the immutable base identity prompt:
```python
BASE_PERSONA_PROMPT = """You are Baby LLM, an evolving, privacy-first personal companion and life success manager.
You operate completely locally on the user's device.
Tone: Warm, intelligent, highly attentive, honest, concise, and focused on helping the user succeed.
Never hallucinate user facts. If you know personal context from your memory, incorporate it naturally.
"""
```

### 1.2 The Working Message Assembly Sequence
The `assemble()` method structures the final chat payload as follows:
1. **System Section 1**: The base persona prompt.
2. **System Section 2 (Verified Personal Context)**: If long-term memories are enabled, `HybridRetriever` retrieves top-$k$ verified active facts:
   ```text
   [Verified Personal Context & Memories]:
   - user lives_in Austin (Category: lifestyle)
   - user allergic_to Penicillin (Category: health)
   ```
3. **System Section 3 (Active Goals & Commitments)**: Active pending commitments with target deadlines are retrieved from SQLite:
   ```text
   [Active User Goals & Commitments]:
   - Launch Project Phoenix (Deadline: 2026-11-01)
   ```
4. **Episodic Recent Turns**: Up to 15 prior turns from the in-memory `EpisodicRingBuffer` are appended as alternating `user` and `assistant` messages.
5. **Current Turn**: The active user message is appended as the terminal `user` message.

---

## 2. Hybrid Retrieval Engine (`HybridRetriever`)

The retrieval layer (`src/baby_llm/retrieval/hybrid.py`) combines the exact lexical precision of BM25 with the conceptual generalization of dense vector embeddings.

### 2.1 Lexical BM25 Search (`BM25Retriever`)
- **Backing Index**: SQLite FTS5 virtual table `memory_fts`.
- **Tokenizer**: `tokenize = 'porter unicode61'`.
- **Query Processing**: Raw user queries are sanitized to alphanumeric tokens, joined as `OR` terms, and evaluated using SQLite's native `bm25(memory_fts)` rank function.
- **Filter**: Only memories with `invalid_from IS NULL` are eligible for recall.

### 2.2 Dense Vector Search (`LocalEmbedder` & `LanceVectorStore`)
- **Embedding Model**: `BAAI/bge-small-en-v1.5` via `fastembed` (ONNX runtime).
- **Dimension**: 384-dimensional normalized float32 vectors.
- **Search Metric**: Cosine similarity (`query.metric("cosine")`) over LanceDB.
- **Filter**: Filtered via `is_active = true` to bypass expired or contradicted facts.

### 2.3 Reciprocal Rank Fusion (RRF) Algorithm
Rather than attempting brittle score normalization across unbounded BM25 scores and cosine distances, Baby LLM uses **Reciprocal Rank Fusion (RRF)**:

$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where:
- $M = \{\text{BM25}, \text{Vector}\}$ is the set of retrieval models.
- $r_m(d)$ is the 1-based rank position of document $d$ in system $m$.
- $k = 60$ is the standard smoothing constant (`settings.rrf_k_constant`).

### 2.4 Spaced Repetition Memory Reinforcement
Crucially, retrieval is not a passive read operation. When an active memory is recalled during a user conversation, `hybrid_retriever.retrieve()` invokes:
```python
self.graph.reinforce_node(node.id)
```
This executes an atomic update in SQLite:
$$\text{stability} \leftarrow \text{stability} \times 2.0$$
$$\text{last\_reinforced\_at} \leftarrow \text{now()}$$

By doubling stability upon every active recall, frequently referenced personal facts become mathematically resistant to temporal decay.

---

## 3. The REM Dream Consolidation Engine (`DreamWorker`)

The **REM Dream Worker** (`src/baby_llm/dream/worker.py`) is an autonomous background thread executing memory consolidation.

### 3.0 Model-to-Model Processing Paradigm
In traditional multi-agent systems, external agents waste expensive frontier model tokens (and seconds of latency) asking LLMs to summarize, index, and organize their own memories. Baby LLM solves this by decoupling memory curation into an asynchronous **Model $\longleftrightarrow$ Model Processing** pipeline:
- An embedded Small Language Model (SLM: `SmolLM2-1.7B` or `Qwen2.5-0.5B`) operates during idle cycles.
- It parses raw dialogue logs from SQLite WAL into atomic Subject-Predicate-Object (SPO) triples, resolves historical contradictions, and applies Ebbinghaus decay math.
- **Result**: External frontier agents (Cursor, Claude, LangGraph) stay focused on task execution and never pay a token or latency tax for memory maintenance.

### 3.1 Triggering Conditions & User Activity Debounce
Consolidation triggers under two conditions:
1. **OS Inactivity**: When elapsed time since the last user turn exceeds `settings.idle_trigger_seconds` (default: 900 seconds / 15 minutes).
2. **Nightly Cron**: During the 03:00 AM window (`settings.dream_cron_hour = 3`), executing once per calendar day.

**User Activity Pause Protocol**: Whenever a chat request hits `/api/chat` or the CLI, `dream_worker.record_user_activity()` sets an internal `_pause_event`. If the consolidation worker is actively processing a batch, it yields immediately, leaving remaining turns in the WAL for the next idle cycle. A 2.0-second timer then clears the pause flag.

### 3.2 Stage 1: Atomic Fact Extraction (`FactExtractor`)
- **Implementation**: `src/baby_llm/dream/extractor.py`
- **Model**: Local quantized SLM (`SmolLM2-1.7B` or `Qwen2.5-0.5B`).
- **Prompt**: Directs the model to parse dialogue into Subject-Predicate-Object (SPO) triples with category and confidence tags:
  ```json
  [
    {
      "subject": "user",
      "predicate": "lives_in",
      "object": "Austin",
      "category": "lifestyle",
      "confidence": 0.95,
      "ymyl": false
    }
  ]
  ```
- **Heuristic Fallback**: If the local model is offline or produces malformed JSON, regular-expression fallback extractors parse key user assertions (`lives_in`, `works_as`, `allergic_to`).

### 3.3 Stage 2: Bi-Temporal Contradiction Resolution (`ConflictResolver`)
- **Implementation**: `src/baby_llm/dream/resolver.py`
- For each extracted triple `(subject, predicate, object)`:
  1. Searches for existing active nodes (`invalid_from IS NULL`) matching `(subject, predicate)`.
  2. **Contradiction Detected** (object differs):
     - Sets the old node's `invalid_from = now()`.
     - Updates the old vector record in LanceDB: `is_active = False`.
     - Inserts the new node with `valid_from = now()`.
     - Computes a new 384-dim embedding and adds it to LanceDB.
  3. **Identical Fact Repeated**:
     - Calls `reinforce_node(old_node.id)`, doubling stability without duplicating records.
  4. **New Fact**:
     - Commits new node to SQLite and embeds to LanceDB.

---

## 4. Scientific Ebbinghaus Decay & YMYL Protection

Human memory naturally decays according to the scientific forgetting curve discovered by Hermann Ebbinghaus. The `EbbinghausDecayEngine` (`src/baby_llm/dream/decay.py`) operationalizes this phenomenon:

### 4.1 The Mathematical Decay Formulation
For any non-YMYL memory node, retention probability $R(t)$ at time $t$ is calculated as:

$$R(t) = \exp\left(-\frac{t}{S \cdot I}\right)$$

Where:
- $t$: Elapsed time in days since `last_reinforced_at`:
  $$t = \max\left(0, \frac{\text{now}() - \text{last\_reinforced\_at}}{86400}\right)$$
- $S$: Memory stability factor (starts at 1.0; doubles on every recall).
- $I$: Domain-specific category importance weight.

```text
┌────────────────────────────────────────────────────────────────────────┐
│            CATEGORY IMPORTANCE WEIGHTS (I) & YMYL RETENTION            │
├────────────────┬────────────────┬─────────────────────┬────────────────┤
│ Category       │ Importance (I) │ Half-Life (S=1.0)   │ YMYL Immunity  │
├────────────────┼────────────────┼─────────────────────┼────────────────┤
│ health         │ 3.0            │ ~2.08 days          │ Yes (R=1.0)    │
│ finance        │ 3.0            │ ~2.08 days          │ Yes (R=1.0)    │
│ goal           │ 2.5            │ ~1.73 days          │ No             │
│ work           │ 2.0            │ ~1.39 days          │ No             │
│ relationship   │ 2.0            │ ~1.39 days          │ No             │
│ lifestyle      │ 1.2            │ ~0.83 days          │ No             │
│ preference     │ 1.0            │ ~0.69 days          │ No             │
└────────────────┴────────────────┴─────────────────────┴────────────────┘
```

### 4.2 Retention Thresholds & Pruning Lifecycle
During each dream consolidation cycle, `evaluate_and_prune()` evaluates all active nodes:
- **Active ($R \ge 0.50$)**: High-fidelity retrieval; prioritized in hybrid RRF.
- **Dormant ($0.20 \le R < 0.50$)**: Lower-priority context; candidate for recall reinforcement.
- **Archived ($R < 0.20$)**: Deactivated. The node's `invalid_from` timestamp is set to `now()` in SQLite, and `is_active = False` is set in LanceDB. The fact is excluded from working context while remaining preserved in the historical trajectory log.

### 4.3 The YMYL (Your Money or Your Life) Shield
Trivial banter (*"I had a cappuccino this morning"*) should fade. Critical life context (*"I am severely allergic to penicillin"*, *"My mortgage is with Chase"*) must **never** be forgotten.

When a memory has `ymyl_protected = True`:
$$R_{\text{YMYL}}(t) \equiv 1.0 \quad \forall t \ge 0$$
The decay engine completely bypasses temporal pruning, guaranteeing 100% permanent retention.

---

## 5. Persona Maturation & The Life Success Engine

Baby LLM is not a static prompt wrapper; it organically evolves as its bi-temporal knowledge graph expands:

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

### 5.1 The Gentle Curiosity Protocol (`GentleCuriosityEngine`)
To prevent the annoying "interrogation trap" of typical chatbots, `src/baby_llm/success/curiosity.py` enforces strict conversational limits:
- **Max Probes**: At most **one** gentle probe per conversation session.
- **Ambiguity Detection**: Scans user inputs using regex for ambiguous named initiatives (e.g. `\bproject\s+([a-zA-Z0-9_\-]+)\b`).
- **Entity Deduplication**: Tracks previously probed entities in `self._asked_entities` so the user is never asked about the same topic twice.

### 5.2 The Personal Success Agent (`PersonalSuccessAgent`)
Operating autonomously via `src/baby_llm/success/agent.py`:
- **07:30 AM Morning Readiness Brief**: Synthesizes the user's top needle-moving commitments into a concise 3-bullet brief. Caches the result in `daily_summaries` to eliminate redundant LLM calls on repeated dashboard visits.
- **Accountability Watchdog**: Evaluates the `commitments` table and alerts the user when a deadline is overdue.
- **21:30 PM Nightly Reflection**: Provides a calm, grounding end-of-day reflection space to capture daily wins and clear mental clutter.

---

## Next Steps
- Review SQLite schemas, LanceDB tables, and encryption mechanics: **[configuration-and-storage.md](configuration-and-storage.md)**
- Explore CLI commands, REST APIs, and MCP tools: **[interfaces-and-api.md](interfaces-and-api.md)**
- Learn about the local test suite and failure recovery: **[development-and-testing.md](development-and-testing.md)**
