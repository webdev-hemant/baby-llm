# 🔌 Interfaces & API Specification

*Interactive CLI Commands, FastAPI REST Endpoints, Model Context Protocol (MCP) Server, and Glass-Box Web Dashboard*

---

## 1. Overview of Interfaces

Baby LLM exposes four unified interfaces, allowing both human operators and external applications to query, update, and inspect personal memory:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   CLI COMMANDS REFERENCE (BABY-LLM)                    │
├────────────────────────────┬───────────────────────────────────────────┤
│ Command Syntax             │ Operational Behavior & Lifecycle          │
├────────────────────────────┼───────────────────────────────────────────┤
│ baby-llm chat              │ Interactive terminal companion session    │
│ baby-llm serve [--port P]  │ Run FastAPI local REST & WebUI server     │
│ baby-llm ui [--port P]     │ Open Glass-Box dashboard in web browser   │
│ baby-llm dream             │ Trigger one-shot REM dream consolidation  │
│ baby-llm memories          │ List active facts with category & YMYL    │
│ baby-llm mcp               │ Run stdio Model Context Protocol server   │
└────────────────────────────┴───────────────────────────────────────────┘
```

---

## 2. Interactive Command-Line Interface (`baby-llm`)

The command-line interface (`src/baby_llm/cli.py`) is registered as `baby-llm` in `pyproject.toml` and can also be executed directly via Python (`python -m baby_llm.cli`).

### 2.1 `baby-llm chat`
Starts an interactive terminal chat session with the local companion:
```bash
.venv/bin/python -m baby_llm.cli chat
```
- **Episodic Memory**: Maintains an in-memory sliding ring buffer of the last 15 conversation turns.
- **Fast-Path Retrieval**: Queries SQLite FTS5 and LanceDB on every turn, injecting relevant memories into the prompt.
- **In-Chat Commands**:
  - `/dream`: Manually triggers background REM dream consolidation and outputs metrics.
  - `exit`, `quit`, `q`: Closes the terminal session.

### 2.2 `baby-llm serve`
Launches the local FastAPI REST API server:
```bash
.venv/bin/python -m baby_llm.cli serve --host 127.0.0.1 --port 21225
```
- **CLI Options**:
  - `--host HOST`: Bind host interface (default: `127.0.0.1` or `BABY_LLM_API_HOST`).
  - `--port PORT`: Port number to bind (default: `21225` or `BABY_LLM_API_PORT`).
- **Background Lifecycle**: Automatically spins up background worker threads for `DreamWorker`, `VaultSyncManager`, and `PersonalSuccessAgent`.

### 2.3 `baby-llm ui`
Opens the default web browser to the running Glass-Box dashboard:
```bash
.venv/bin/python -m baby_llm.cli ui --port 21225
```

### 2.4 `baby-llm dream`
Executes an immediate one-shot REM Dream consolidation cycle headlessly:
```bash
.venv/bin/python -m baby_llm.cli dream
```
Output:
```text
REM Dream Cycle Completed: {'turns_processed': 4, 'facts_extracted': 3, 'nodes_archived': 0, 'active_nodes_count': 12}
```

### 2.5 `baby-llm memories`
Prints all currently active facts from the bi-temporal knowledge graph:
```bash
.venv/bin/python -m baby_llm.cli memories
```
Output:
```text
🧠 Baby LLM Active Memories (3 facts):
------------------------------------------------------------
• [LIFESTYLE] user lives_in Austin
  Confidence: 95% | Stability: 2.0 | ID: 3c8e41bf
• [HEALTH] user allergic_to Penicillin [🛡️ YMYL]
  Confidence: 100% | Stability: 1.0 | ID: 8a1b2c3d
• [GOAL] user goal_is launch Project Phoenix
  Confidence: 95% | Stability: 1.0 | ID: 9f0e1d2c
------------------------------------------------------------
```

### 2.6 `baby-llm mcp`
Launches the Model Context Protocol (MCP) server over standard I/O (`stdio`) for integration into Cursor IDE and Claude Desktop.

---

## 3. FastAPI REST API Specification

The REST server (`src/baby_llm/api/server.py`) operates by default on **Port 21225** (`B-A-B-Y`).

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     FASTAPI REST ENDPOINTS SUMMARY                     │
├───────────────────────────┬────────────────────┬───────────────────────┤
│ Method & Path             │ Request / Params   │ Operational Purpose   │
├───────────────────────────┼────────────────────┼───────────────────────┤
│ GET /api/health           │ None               │ Liveness probe        │
│ POST /api/chat            │ ChatRequest JSON   │ Fast-path inference   │
│ GET /api/memories         │ category, active   │ List memory nodes     │
│ POST /api/memories        │ MemoryCreate JSON  │ Manual fact commit    │
│ PUT /api/memories/{id}    │ MemoryUpdate JSON  │ In-place fact update  │
│ DELETE /api/memories/{id} │ Path node_id       │ One-click fact erase  │
│ POST /api/dream/trigger   │ None               │ Trigger REM dream     │
│ GET /api/success/compass  │ None               │ Morning brief & goals │
└───────────────────────────┴────────────────────┴───────────────────────┘
```

### 3.1 Static Routes & PWA Hosting
- `GET /`: Serves `ui/index.html`.
- `GET /styles.css`: Serves glassmorphic design system stylesheets.
- `GET /app.js`: Serves frontend application JavaScript.
- `GET /manifest.json`: Serves PWA standalone application manifest.
- `GET /icon.svg`: Serves application branding icon.
- `GET /ui`: Mounted static directory serving all dashboard assets.

---

### 3.2 Endpoints Deep Dive

#### `GET /api/health`
Health check and liveness probe.
- **Response**: `200 OK`
  ```json
  {
    "status": "awake",
    "version": "0.1.0",
    "timestamp": "2026-10-13T01:00:00+00:00"
  }
  ```
- **Example**:
  ```bash
  curl -s http://127.0.0.1:21225/api/health
  ```

---

#### `POST /api/chat`
Real-time Fast-Path conversational inference with memory attribution.
- **Request Body (`ChatRequest`)**:
  ```json
  {
    "message": "What city do I live in and what are my current priorities?",
    "session_id": "default",
    "stream": false,
    "incognito": false
  }
  ```
- **Behavior**:
  - `incognito: false`: Context is assembled, response is generated, Gentle Curiosity is evaluated, and the turn is committed to SQLite WAL.
  - `incognito: true`: Context is assembled and response is generated, but **WAL interaction logging and curiosity probing are completely bypassed**.
- **Response**: `200 OK`
  ```json
  {
    "turn_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "reply": "You live in Austin, Texas. Your active priority is launching Project Phoenix.",
    "probed": false,
    "incognito": false
  }
  ```
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:21225/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "I prefer dark mode in all my IDEs."}'
  ```

---

#### `GET /api/memories`
Retrieves stored memory nodes for Glass-Box inspection.
- **Query Parameters**:
  - `category` *(optional)*: Filter by `lifestyle`, `health`, `finance`, `work`, `relationship`, `goal`, or `preference`.
  - `active_only` *(optional, default `true`)*: If `true`, returns only active facts (`invalid_from IS NULL`).
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "3c8e41bf-e3db-4cb8-8254-6e6556e828e8",
      "fact": "user lives_in Austin",
      "subject": "user",
      "predicate": "lives_in",
      "object": "Austin",
      "category": "lifestyle",
      "confidence": 0.95,
      "stability": 2.0,
      "is_active": true,
      "ymyl_protected": false,
      "valid_from": "2026-10-13T01:00:00+00:00",
      "invalid_from": null
    }
  ]
  ```
- **Example**:
  ```bash
  curl -s "http://127.0.0.1:21225/api/memories?category=health"
  ```

---

#### `POST /api/memories`
Explicitly creates or overrides a memory node from the UI or external script.
- **Request Body (`MemoryCreateRequest`)**:
  ```json
  {
    "subject": "user",
    "predicate": "allergic_to",
    "object": "Penicillin",
    "category": "health",
    "confidence": 1.0,
    "ymyl_protected": true
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "status": "success",
    "id": "8a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
    "fact": "user allergic_to Penicillin"
  }
  ```
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:21225/api/memories \
    -H "Content-Type: application/json" \
    -d '{"subject": "user", "predicate": "works_at", "object": "Anthropic", "category": "work"}'
  ```

---

#### `PUT /api/memories/{node_id}`
In-place update of an existing memory node. Invalidates the prior node in the bi-temporal graph and commits the updated node.
- **Request Body (`MemoryUpdateRequest`)**:
  ```json
  {
    "object": "Tokyo",
    "category": "lifestyle"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "status": "updated",
    "id": "new-node-uuid",
    "old_id": "old-node-uuid",
    "fact": "user lives_in Tokyo"
  }
  ```
- **Example**:
  ```bash
  curl -X PUT http://127.0.0.1:21225/api/memories/3c8e41bf-e3db-4cb8-8254-6e6556e828e8 \
    -H "Content-Type: application/json" \
    -d '{"object": "Tokyo"}'
  ```

---

#### `DELETE /api/memories/{node_id}`
Permanently erases a memory node from both SQLite (including FTS5) and LanceDB.
- **Response**: `200 OK`
  ```json
  {
    "status": "deleted",
    "id": "3c8e41bf-e3db-4cb8-8254-6e6556e828e8"
  }
  ```
- **Example**:
  ```bash
  curl -X DELETE http://127.0.0.1:21225/api/memories/3c8e41bf-e3db-4cb8-8254-6e6556e828e8
  ```

---

#### `POST /api/dream/trigger`
Forces an immediate REM Dream memory consolidation cycle.
- **Response**: `200 OK`
  ```json
  {
    "status": "completed",
    "summary": {
      "turns_processed": 2,
      "facts_extracted": 2,
      "nodes_archived": 0,
      "active_nodes_count": 8
    }
  }
  ```
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:21225/api/dream/trigger
  ```

---

#### `GET /api/success/compass`
Retrieves active personal success directives, morning briefs, and alerts.
- **Response**: `200 OK`
  ```json
  {
    "morning_brief": "🌅 Good morning! Top priority: Launch Project Phoenix by Nov 1.",
    "commitments": [
      {
        "id": "c1",
        "title": "Launch Project Phoenix",
        "status": "pending",
        "deadline": "2026-11-01T00:00:00"
      }
    ],
    "alerts": []
  }
  ```
- **Example**:
  ```bash
  curl -s http://127.0.0.1:21225/api/success/compass
  ```

---

## 4. Universal Model Context Protocol (MCP) Server

The Universal MCP Server (`src/baby_llm/mcp/server.py`) implements the Model Context Protocol using FastMCP over standard I/O (`stdio`).

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      UNIVERSAL MCP TOOLS SUMMARY                       │
├───────────────────┬─────────────────────────┬──────────────────────────┤
│ Tool Name         │ Arguments               │ Return Description       │
├───────────────────┼─────────────────────────┼──────────────────────────┤
│ recall_memory     │ query: str, top_k: int  │ Matching verified facts  │
│ commit_fact       │ subject, pred, obj, cat │ Committed fact node ID   │
│ get_active_goals  │ None                    │ Active user commitments  │
│ record_daily_win  │ note: str               │ Daily win accomplishment │
└───────────────────┴─────────────────────────┴──────────────────────────┘
```

### 4.1 Exposed MCP Tool Specifications

#### 1. `recall_memory(query: str, top_k: int = 5) -> str`
Executes hybrid RRF retrieval over SQLite FTS5 and LanceDB to surface verified personal context.
- **Example Output**:
  ```text
  - [LIFESTYLE] user lives_in Austin (Confidence: 95%, Source: hybrid)
  - [GOAL] user goal_is launch Project Phoenix (Confidence: 95%, Source: vector)
  ```

#### 2. `commit_fact(subject: str, predicate: str, object_: str, category: str = "preference", ymyl_protected: bool = False) -> str`
Explicitly commits a fact to the bi-temporal knowledge graph with automatic contradiction resolution and dense vector indexing.
- **Example Output**:
  ```text
  Successfully committed memory node: user prefers dark_mode (ID: 7a8b9c0d-...)
  ```

#### 3. `get_active_goals() -> str`
Lists all active goals and commitments tracked in the state machine.
- **Example Output**:
  ```text
  - [PENDING] Launch Project Phoenix [Due: 2026-11-01]
  - [IN_PROGRESS] Refactor SQLite WAL schema
  ```

#### 4. `record_daily_win(note: str) -> str`
Records an accomplishment or breakthrough for the current day.
- **Example Output**:
  ```text
  Recorded accomplishment: 'Completed Milestone 4 MCP documentation'
  ```

---

## 5. Glass-Box Web Dashboard (`ui/`)

Baby LLM includes a standalone, zero-framework web dashboard built with HTML5, Vanilla JavaScript (`ui/app.js`), and Glassmorphic CSS (`ui/styles.css`).

### 5.1 Dashboard Views
1. **Interactive Companion Tab (`#view-chat`)**: Real-time conversational interface with memory attribution indicator bubbles, a typing placeholder, and an **Incognito Toggle Pill** that bypasses WAL logging for sensitive queries.
2. **Mindstream Vault Tab (`#view-mindstream`)**: Transparent visual card grid displaying all active facts, categorized by pills (`All`, `Lifestyle`, `Health`, `Finance`, `Work`, `Relationship`, `Goal`, `Preference`). Each card displays confidence score, stability metric, YMYL shield indicator, and inline **Edit** and **Erase** buttons.
3. **Bi-Temporal Timeline Tab (`#view-timeline`)**: Displays the historical trajectory of facts over time, showing active facts in green alongside archived/overwritten historical facts in muted gray.
4. **Success Compass Sidebar**: Surfaces the cached 07:30 AM Morning Brief, active commitments with clickable checkboxes, and the **Trigger Dream** button with real-time VRAM status indicators.

---

## Next Steps
- Learn about testing, verification, and extending Baby LLM: **[development-and-testing.md](development-and-testing.md)**
- Review storage schemas and encryption: **[configuration-and-storage.md](configuration-and-storage.md)**
- Review core engine and decay curves: **[core-engine.md](core-engine.md)**
