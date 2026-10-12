# Milestone 4: Proactive Success Agent & Local Ecosystem Sync
*Weeks 10 – 12 • Primary Objective: Proactive Life Loops, Vault Sync & Security Hardening*

---

## 1. Executive Summary & Objective

The primary objective of **Milestone 4** is to transform Baby LLM from a passive storage utility into an active, proactive personal success companion:
1. **Personal Success Loops**: Automated morning focus briefs (07:30 AM), accountability watchdog checks for overdue commitments, and nightly frictionless mental downloads (09:30 PM).
2. **Gentle Curiosity Protocol**: Proactively yet unobtrusively asks at most one clarifying question per session when encountering ambiguous entities (e.g. "Project Alpha").
3. **Bidirectional Obsidian Vault Synchronization**: Automatically translates learned memory nodes into local Markdown files with YAML frontmatter at `~/BabyLLM/vault/memories/`, listening for external edits via `watchdog` to synchronize changes back into SQLite and LanceDB.
4. **Security Hardening**: Protects sensitive financial and medical YMYL attributes using AES-GCM-256 encryption backed by the OS Keyring.
5. **Unified CLI Suite**: Provides streamlined user terminal commands (`baby-llm chat`, `baby-llm serve`, `baby-llm ui`, `baby-llm dream`, `baby-llm memories`, `baby-llm mcp`).

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROACTIVE SUCCESS & SYNC ARCHITECTURE                    │
├──────────────────────────────────────────────┬──────────────────────────────┤
│ Proactive Success Loops                      │ Local Ecosystem Vault Sync   │
│ • Morning Intention Brief (07:30 AM)         │ • ~/BabyLLM/vault/memories/  │
│ • Nightly Reflection & Unload (09:30 PM)     │ • Bidirectional watchdog     │
│ • Accountability Watchdog (Overdue alerts)   │ • Markdown frontmatter parse │
├──────────────────────────────────────────────┴──────────────────────────────┤
│ Gentle Curiosity Protocol & Security Shield                                 │
│ • Single gentle probe per session for ambiguous entities                    │
│ • AES-GCM-256 encryption of YMYL memory nodes via OS Keyring                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Layout & Module Map

| Module Path | Primary Symbols / Classes | Responsibility |
| :--- | :--- | :--- |
| [`src/baby_llm/success/agent.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/agent.py) | [`PersonalSuccessAgent`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/agent.py#L13) | Morning readiness brief, evening reflection, and overdue watchdog |
| [`src/baby_llm/success/tracker.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/tracker.py) | [`SuccessTracker`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/tracker.py#L11) | State machine managing commitments and goals |
| [`src/baby_llm/success/curiosity.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/curiosity.py) | [`GentleCuriosityEngine`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/curiosity.py#L7) | Enforces 1-probe-per-session limit on ambiguous entities |
| [`src/baby_llm/sync/obsidian_sync.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/sync/obsidian_sync.py) | [`VaultSyncManager`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/sync/obsidian_sync.py#L15), [`VaultWatchdogHandler`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/sync/obsidian_sync.py#L83) | Bidirectional markdown serialization and watchdog listener |
| [`src/baby_llm/cli.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/cli.py) | [`main()`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/cli.py#L81) | CLI subcommands and parameter parser |

---

## 3. Storage Schema & Serialization Format

### 3.1 Commitments & Daily Summaries SQLite Tables
```sql
CREATE TABLE IF NOT EXISTS commitments (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'dropped')) DEFAULT 'pending',
    target_deadline TIMESTAMP,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    associated_node_id TEXT REFERENCES memory_nodes(id)
);

CREATE TABLE IF NOT EXISTS daily_summaries (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL UNIQUE,
    summary_type TEXT CHECK(summary_type IN ('morning_brief', 'evening_reflection')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 Obsidian Markdown Vault Frontmatter Schema
Each memory node exported to `~/BabyLLM/vault/memories/{node_id}.md` adheres to the following structure:
```markdown
---
id: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
subject: "user"
predicate: "lives_in"
object: "Austin"
category: "lifestyle"
confidence: 0.95
ymyl_protected: false
valid_from: "2026-10-12T10:00:00"
---

# User lives in Austin

*Stored by Baby LLM in the Bi-Temporal Memory Graph.*
```

---

## 4. Implementation Tasks & Deliverables

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MILESTONE 4 IMPLEMENTATION CHECKLIST                     │
├──────┬─────────────────────────────────────────────────┬────────────────────┤
│ Item │ Task Description                                │ Verification       │
├──────┼─────────────────────────────────────────────────┼────────────────────┤
│ 4.1  │ Morning brief (07:30) & reflection synthesis    │ test_agent_loop    │
│ 4.2  │ Commitments state-machine and watchdog alerts   │ test_tracker.py    │
│ 4.3  │ Gentle Curiosity protocol (1 probe / session)   │ test_curiosity.py  │
│ 4.4  │ Markdown YAML serialization & import parser     │ test_vault_sync    │
│ 4.5  │ Live Watchdog background filesystem observer    │ test_observer_loop │
│ 4.6  │ Autonomous background cron/scheduler daemon     │ test_scheduler     │
│ 4.7  │ AES-GCM-256 encryption via OS Keyring           │ test_encryption    │
│ 4.8  │ CLI packaging suite (including baby-llm ui)     │ CLI entry tests    │
└──────┴─────────────────────────────────────────────────┴────────────────────┘
```

---

## 5. Verification Gates & Automated Test Suites

### 5.1 Verification Gate
* **Gate G7 (Air-Gapped Privacy & Local Security)**: 0 outbound external calls; AES-GCM-256 encrypted storage of YMYL items using keys held in the local OS Keyring.

### 5.2 Test Coverage
* Unit tests for [`PersonalSuccessAgent`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/agent.py#L13) and [`SuccessTracker`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/tracker.py#L11).
* Verification of [`GentleCuriosityEngine`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/curiosity.py#L7) session resetting and single-probe budget enforcement.
* Bidirectional markdown roundtrip verification: writing `.md` file with modified object updates SQLite and LanceDB automatically.

---

## 6. Current Implementation Status & Outstanding Work

* **Completed (50%)**:
  * Morning intention brief synthesis with SQLite daily summary caching is implemented in [`src/baby_llm/success/agent.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/agent.py).
  * Commitment CRUD operations and status transitions are implemented in [`src/baby_llm/success/tracker.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/tracker.py).
  * Gentle Curiosity engine is implemented in [`src/baby_llm/success/curiosity.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/success/curiosity.py) and integrated into both the CLI chat loop and the FastAPI `/api/chat` route.
  * Vault Markdown export and YAML safe-loading logic are written in [`src/baby_llm/sync/obsidian_sync.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/sync/obsidian_sync.py).
* **Remaining Action Items**:
  * Wire the `watchdog.observers.Observer` instance to actively run in the background upon service startup (`baby-llm serve`).
  * Implement an active background scheduling loop (e.g. APScheduler or asyncio cron loop) to trigger morning and evening briefs without requiring manual endpoint requests.
  * Implement AES-GCM-256 attribute-level encryption for YMYL nodes using the system keyring.
  * Add the `baby-llm ui` CLI subcommand to automatically open the default browser at `http://127.0.0.1:21225`.
