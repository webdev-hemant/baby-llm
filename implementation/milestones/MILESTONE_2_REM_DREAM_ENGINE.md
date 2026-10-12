# Milestone 2: The REM Dream Engine & Bi-Temporal Graph
*Weeks 4 – 6 • Primary Objective: Asynchronous Background Memory Consolidation & Decay*

---

## 1. Executive Summary & Objective

The primary objective of **Milestone 2** is to build the cognitive consolidation engine known as the **"REM Dream" worker**. 

Stateless LLMs forget interactions immediately, while standard RAG stores accumulate conflicting noise. Baby LLM solves this by processing conversation logs asynchronously during device idle periods or scheduled night cycles (03:00 AM):
1. **Fact Extraction**: Extracts durable atomic Subject-Predicate-Object (SPO) triples from dialogue turns.
2. **Bi-Temporal Contradiction Resolution**: Detects updates or conflicts (e.g. "I moved to Austin" vs. "I live in Seattle"), closing the validity window of previous nodes while recording new ones.
3. **Scientific Memory Decay**: Calculates Ebbinghaus forgetting curves to let conversational trivia fade while protecting critical health and financial context (YMYL shield).

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       REM DREAM CONSOLIDATION PIPELINE                      │
└─────────────────────────────────────────────────────────────────────────────┘

  SQLite interaction_log (Unprocessed Turns)
            │
            ▼
  [Step A] Atomic SPO Extraction (Qwen2.5-0.5B-Instruct SLM)
            │ Outputs: [{subject, predicate, object, category, ymyl}]
            ▼
  [Step B] Bi-Temporal Contradiction Resolver
            ├─ Existing fact matches? ──► Reinforce stability (S = S * 2)
            ├─ Contradiction found?   ──► Set old invalid_from = now
            └─ Insert new active node ──► Write to SQLite & LanceDB
            │
            ▼
  [Step C] Ebbinghaus Retention & Decay Calculator
            ├─ Calculate R(t) = exp(-t / (S * I))
            ├─ If ymyl_protected == 1 ──► R(t) = 1.0 (Immune from decay)
            ├─ If R(t) >= 0.50        ──► Active memory
            ├─ If 0.20 <= R(t) < 0.50 ──► Dormant memory
            └─ If R(t) < 0.20         ──► Archive & remove from vector index
```

---

## 2. Component Layout & Module Map

| Module Path | Primary Symbols / Classes | Responsibility |
| :--- | :--- | :--- |
| [`src/baby_llm/storage/graph_store.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/storage/graph_store.py) | [`BiTemporalGraphStore`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/storage/graph_store.py#L9) | CRUD operations, historical trajectories, and FTS5 synchronization |
| [`src/baby_llm/dream/extractor.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/dream/extractor.py) | [`FactExtractor`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/dream/extractor.py#L32) | Extracts atomic SPO triples using SLM prompt and regex fallback |
| [`src/baby_llm/dream/resolver.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/dream/resolver.py) | [`ConflictResolver`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/dream/resolver.py#L11) | Detects contradictions and updates `valid_from` / `invalid_from` |
| [`src/baby_llm/dream/decay.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/dream/decay.py) | [`EbbinghausDecayEngine`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/dream/decay.py#L11) | Computes $R(t)$ retention probability and manages YMYL immunity |
| [`src/baby_llm/dream/worker.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/dream/worker.py) | [`DreamWorker`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/dream/worker.py#L13) | Coordinates ingestion, extraction, resolution, and decay pruning |

---

## 3. Storage Schema & Mathematical Formulations

### 3.1 Bi-Temporal Relational Schema
```sql
CREATE TABLE IF NOT EXISTS memory_nodes (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    category TEXT CHECK(category IN ('lifestyle', 'health', 'finance', 'work', 'relationship', 'goal', 'preference')),
    confidence REAL DEFAULT 1.0,
    stability REAL DEFAULT 1.0,
    last_reinforced_at TIMESTAMP NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    invalid_from TIMESTAMP,                   -- NULL denotes active; timestamp denotes closed
    ymyl_protected BOOLEAN DEFAULT 0,         -- 1 = Immune from temporal decay
    source_turn_id TEXT REFERENCES interaction_log(turn_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_memory_active ON memory_nodes (invalid_from) WHERE invalid_from IS NULL;
CREATE INDEX IF NOT EXISTS idx_memory_category ON memory_nodes (category);
CREATE INDEX IF NOT EXISTS idx_memory_subject ON memory_nodes (subject);
```

### 3.2 Scientific Ebbinghaus Forgetting & Decay Model
The retention probability $R(t)$ of any memory node at elapsed time $t$ (days) since reinforcement is given by:

$$R(t) = \exp\left( -\frac{t}{S \cdot I} \right)$$

Where:
* $t$: Elapsed days since `last_reinforced_at`.
* $S$: Memory Stability (starts at $1.0$, doubles to $S \times 2.0$ whenever referenced or recalled).
* $I$: Importance Weight according to category:
  * Health / Finance (YMYL): $I = 3.0$
  * Goal: $I = 2.5$
  * Work / Relationship: $I = 2.0$
  * Lifestyle: $I = 1.2$
  * Preference: $I = 1.0$
* **YMYL Immunity Shield**: If `ymyl_protected == 1`, $R(t) \equiv 1.0$ unconditionally.
* **Pruning and Index Policy**:
  * $R(t) \ge 0.50$: Node is **Active** (included in fast-path context and LanceDB).
  * $0.20 \le R(t) < 0.50$: Node is **Dormant** (retained in SQLite, excluded from standard vector top-k).
  * $R(t) < 0.20$: Node is **Archived** (invalidated in SQLite and deactivated in LanceDB).

---

## 4. Implementation Tasks & Deliverables

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MILESTONE 2 IMPLEMENTATION CHECKLIST                    │
├──────┬─────────────────────────────────────────────────┬────────────────────┤
│ Item │ Task Description                                │ Verification       │
├──────┼─────────────────────────────────────────────────┼────────────────────┤
│ 2.1  │ Bi-temporal table schema & migrations           │ test_graph_store   │
│ 2.2  │ SLM Atomic SPO extractor with JSON schema       │ Extractor fixture  │
│ 2.3  │ Heuristic regex fallback for offline extractor  │ Heuristic tests    │
│ 2.4  │ Bi-temporal contradiction resolver              │ test_graph_store   │
│ 2.5  │ Ebbinghaus decay calculator with YMYL shield    │ test_decay.py      │
│ 2.6  │ Dream consolidation cycle coordinator           │ test_dream_cycle   │
│ 2.7  │ Autonomous OS idle listener & scheduler loop    │ Daemon worker test │
└──────┴─────────────────────────────────────────────────┴────────────────────┘
```

---

## 5. Verification Gates & Automated Test Suites

### 5.1 Verification Gates
* **Gate G2 (Contradiction Accuracy)**: > 95% accuracy in closing superseded facts and preserving new ones on synthetic conflict scenarios.
* **Gate G3 (Memory Decay Mathematics)**: Calculated retention strictly matches the scientific Ebbinghaus curve.
* **Gate G4 (YMYL Immunity)**: 100% retention floor for protected health, financial, and core value nodes.
* **Gate G5 (Background Resource Ceiling)**: Background dream worker memory consumption stays strictly under 1.0GB RAM/VRAM.

### 5.2 Test Coverage
* [`tests/unit/test_graph_store.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/unit/test_graph_store.py):
  * `test_insert_and_retrieve_node()`: Verifies basic node insertion.
  * `test_bi_temporal_invalidation_and_history()`: Validates temporal invalidation and trajectory queries.
  * `test_reinforce_node()`: Verifies stability doubling.
* [`tests/unit/test_decay.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/unit/test_decay.py):
  * `test_ymyl_retention_floor()`: Confirms $R(t) = 1.0$ regardless of elapsed time.
  * `test_ebbinghaus_decay_curve()`: Verifies exponential decay over 30 days.
  * `test_stability_extension()`: Verifies extended retention when stability increases.
* [`tests/integration/test_dream_cycle.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/integration/test_dream_cycle.py):
  * `test_full_dream_consolidation_and_contradiction()`: Simulates end-to-end conversation ingestion, extraction, contradiction resolution, and decay pruning.
  * `test_dream_worker_background_daemon()`: Validates autonomous idle background thread execution, user activity pause, and graceful termination.

---

## 6. Current Implementation Status & Outstanding Work

* **Completed (100%)**:
  * Bi-temporal graph store, SPO fact extractor, contradiction resolver, and Ebbinghaus decay engine are completely implemented and pass all tests.
  * Autonomous background daemon thread implemented in [`worker.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/dream/worker.py) monitoring OS idle threshold and 03:00 AM nightly cron, with immediate concurrency pause on user activity.
  * Full consolidation cycle callable programmatically, via background daemon, and via CLI (`baby-llm dream`).
  * Automated integration test suite updated and passing (17/17 tests across the project).
* **Remaining Action Items**:
  * None. Milestone 2 is 100% complete, verified, and ready for Milestone 3 Universal MCP & Glass-Box UI integration.
