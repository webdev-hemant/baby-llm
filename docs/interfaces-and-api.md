# 🔌 Interfaces & API Specification

*Universal Model Context Protocol (MCP), FastAPI REST Agent Bus, Interactive CLI, and Glass-Box Web Dashboard*

---

## 1. Overview of Interfaces

Baby LLM provides four unified interfaces designed to serve both autonomous AI agents and human operators:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   BABY LLM INTERFACES ARCHITECTURE                     │
├────────────────────────────┬────────────────────┬──────────────────────┤
│ Surface                    │ Protocol / Binding │ Primary Audience     │
├────────────────────────────┼────────────────────┼──────────────────────┤
│ 1. Universal FastMCP       │ stdio JSON-RPC     │ Cursor, Claude, IDEs │
│ 2. FastAPI REST Server     │ HTTP Port 21225    │ Python Agent Swarms  │
│ 3. Interactive CLI         │ Terminal TTY       │ Developer Operators  │
│ 4. Glass-Box Dashboard     │ PWA / Web Browser  │ Human Oversight      │
└────────────────────────────┴────────────────────┴──────────────────────┘
```

---

## 2. Universal Model Context Protocol (MCP) — Primary Agent Interface

The **Model Context Protocol (MCP)** server (`src/baby_llm/mcp/server.py`) is Baby LLM's primary external integration surface. It exposes your local bi-temporal memory graph and hybrid retrieval engine directly to **Cursor IDE**, **Claude Desktop**, and autonomous agent loops over standard input/output (`stdio`).

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   UNIVERSAL MCP SERVER ARCHITECTURE                    │
└────────────────────────────────────────────────────────────────────────┘

 [Cursor IDE / Claude Desktop / External Agent]
               │
               ▼ (stdio JSON-RPC protocol)
┌────────────────────────────────────────────────────────────────────────┐
│ baby-llm mcp (FastMCP Server: baby-llm-mcp)                            │
│   ├─ recall_memory(query, top_k)                                       │
│   ├─ commit_fact(subject, predicate, object, category, ymyl)           │
│   ├─ get_active_goals()                                                │
│   └─ record_daily_win(note)                                            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
  [Local SQLite Knowledge Graph & LanceDB Vector Store (~/.baby_llm/)]
```

### 2.1 Available MCP Tool Primitives

Baby LLM registers four high-level tools via FastMCP:

#### Tool 1: `recall_memory`
Retrieves verified personal and project facts matching a semantic query in sub-30ms using Reciprocal Rank Fusion (RRF).
- **Arguments**:
  - `query` (`string`, required): Natural language search query (e.g., `"Project Phoenix database choice"`).
  - `top_k` (`integer`, optional, default: `5`): Maximum number of memories to return.
- **Return Value**:
  Formatted list of verified facts with category and confidence score:
  ```text
  - [GOAL] user goal_is launch Project Phoenix (Confidence: 95%, Source: hybrid)
  - [WORK] user tech_stack FastAPI LanceDB SQLite (Confidence: 100%, Source: bm25)
  - [PREFERENCE] user avoids TailwindCSS (Confidence: 90%, Source: vector)
  ```

#### Tool 2: `commit_fact`
Allows an external agent to explicitly commit or update a structured fact in the bi-temporal knowledge graph.
- **Arguments**:
  - `subject` (`string`, required): The entity subject (e.g., `"project_phoenix"`).
  - `predicate` (`string`, required): The relationship predicate (e.g., `"uses_database"`).
  - `object_` (`string`, required): The target value (e.g., `"sqlite_lancedb"`).
  - `category` (`string`, optional, default: `"preference"`): One of `identity`, `preference`, `relationship`, `work`, `lifestyle`, `health`, `finance`, `goal`.
  - `ymyl_protected` (`boolean`, optional, default: `false`): If true, fact receives infinite retention and AES-GCM-256 encryption.
- **Return Value**:
  `Successfully committed memory node: project_phoenix uses_database sqlite_lancedb (ID: a1b2c3d4)`

#### Tool 3: `get_active_goals`
Surfaces all active personal and project commitments currently tracked by the success engine.
- **Arguments**: None.
- **Return Value**:
  ```text
  - [IN_PROGRESS] Launch Project Phoenix beta [Due: 2026-11-01]
  - [PENDING] Complete code review for PR #126
  ```

#### Tool 4: `record_daily_win`
Allows an agent to record an accomplishment or breakthrough on behalf of the user.
- **Arguments**:
  - `note` (`string`, required): Description of the accomplishment (e.g., `"Refactored MCP server to support streaming"`).
- **Return Value**:
  `Recorded accomplishment: 'Refactored MCP server to support streaming'`

---

### 2.2 Client Configuration

#### Configuration for Claude Desktop
Add the following to your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

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

#### Configuration for Cursor IDE
1. Open Cursor Settings (`Cmd + ,` or `Ctrl + ,`).
2. Navigate to **Features** -> **MCP**.
3. Click **+ Add New MCP Server**.
4. Configure the server parameters:
   - **Name**: `baby-llm`
   - **Type**: `command`
   - **Command**: `/Users/admin/Desktop/corporate/projects/baby-llm/.venv/bin/python -m baby_llm.cli mcp`
5. Click **Save** and verify the green status indicator.

---

### 2.3 Programmatic Python Agent Client
External Python agents (e.g., LangGraph, CrewAI, AutoGen) can launch and communicate with `baby-llm mcp` directly:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="/Users/admin/Desktop/corporate/projects/baby-llm/.venv/bin/python",
    args=["-m", "baby_llm.cli", "mcp"],
)

async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Recall relevant context
            result = await session.call_tool("recall_memory", {"query": "Project Phoenix architecture"})
            print("Recalled Memory:\n", result.content[0].text)
            
            # Commit new architectural decision
            commit_res = await session.call_tool("commit_fact", {
                "subject": "project_phoenix",
                "predicate": "implements",
                "object_": "mcp_memory_substrate",
                "category": "work"
            })
            print(commit_res.content[0].text)

asyncio.run(run_agent())
```

---

## 3. FastAPI REST API Specification (Agent HTTP Bus)

The REST server (`src/baby_llm/api/server.py`) runs by default on **Port 21225** (`B-A-B-Y`). It acts as an HTTP agent memory bus for web applications, microservices, and distributed agent swarms.

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

### 3.1 Endpoints Specification

#### 1. `GET /api/health`
- **Purpose**: System liveness check.
- **Response**: `{"status": "ok", "version": "0.1.0"}`

#### 2. `POST /api/chat`
- **Purpose**: Fast-path conversational inference. Context assembly occurs in <20ms, and the interaction turn is immediately appended to SQLite WAL.
- **Request Body**:
  ```json
  {
    "message": "What is our architecture policy for Project Phoenix?",
    "session_id": "agent-session-101"
  }
  ```
- **Response**:
  ```json
  {
    "response": "Project Phoenix enforces 100% offline local memory using SQLite FTS5 and LanceDB.",
    "session_id": "agent-session-101"
  }
  ```

#### 3. `GET /api/memories`
- **Purpose**: Retrieve active memory nodes. Supports filtering by category and active status.
- **Query Parameters**:
  - `category` (optional, string): Filter by category (`identity`, `work`, `health`, etc.).
  - `active_only` (optional, boolean, default: `true`): Return only valid facts.
- **Response**:
  ```json
  [
    {
      "id": "c7b1a2e3",
      "subject": "project_phoenix",
      "predicate": "implements",
      "object": "fastmcp_stdio_server",
      "category": "work",
      "confidence": 1.0,
      "stability": 2.0,
      "ymyl_protected": false,
      "valid_from": "2026-10-13T01:30:00Z",
      "invalid_from": null
    }
  ]
  ```

#### 4. `POST /api/memories`
- **Purpose**: Create or resolve a memory node in the knowledge graph.
- **Request Body**:
  ```json
  {
    "subject": "user",
    "predicate": "prefers_editor",
    "object": "Cursor IDE",
    "category": "preference"
  }
  ```
- **Response**: Status `200 OK` with full committed `MemoryNode` object.

#### 5. `DELETE /api/memories/{node_id}`
- **Purpose**: Erase a memory node permanently. Updates SQLite and LanceDB immediately.
- **Response**: `{"status": "deleted", "id": "c7b1a2e3"}`

#### 6. `POST /api/dream/trigger`
- **Purpose**: Trigger an immediate headless REM dream consolidation cycle.
- **Response**:
  ```json
  {
    "status": "completed",
    "turns_processed": 5,
    "facts_extracted": 3,
    "nodes_archived": 1,
    "active_nodes_count": 14
  }
  ```

#### 7. `GET /api/success/compass`
- **Purpose**: Retrieve today's Morning Readiness Brief and active commitments.
- **Response**:
  ```json
  {
    "morning_brief": "Good morning! Focus on Project Phoenix beta release today.",
    "active_commitments": [
      {
        "id": "commit-1",
        "title": "Project Phoenix beta deployment",
        "status": "in_progress",
        "target_deadline": "2026-10-13T23:59:59Z"
      }
    ]
  }
  ```

---

### 3.2 Python HTTP Agent Client (`httpx`)
Agents can query and commit memories over HTTP with three lines of Python:

```python
import httpx

BASE_URL = "http://127.0.0.1:21225"

# 1. Fetch active memories
with httpx.Client(base_url=BASE_URL) as client:
    res = client.get("/api/memories", params={"category": "work"})
    memories = res.json()
    print(f"Loaded {len(memories)} work memories.")

    # 2. Commit a new fact
    commit_res = client.post("/api/memories", json={
        "subject": "project_phoenix",
        "predicate": "status",
        "object": "feature_complete",
        "category": "work"
    })
    print("Committed:", commit_res.json()["id"])
```

---

## 4. Interactive Command-Line Interface (`baby-llm`)

The command-line interface (`src/baby_llm/cli.py`) is registered as `baby-llm` in `pyproject.toml` and can also be executed directly via Python (`python -m baby_llm.cli`).

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

### 4.1 `baby-llm chat`
Starts an interactive terminal chat session with the local companion:
```bash
.venv/bin/python -m baby_llm.cli chat
```
- **Episodic Memory**: Maintains an in-memory sliding ring buffer of the last 15 conversation turns.
- **Fast-Path Retrieval**: Queries SQLite FTS5 and LanceDB on every turn, injecting relevant memories into the prompt.
- **In-Chat Commands**:
  - `/dream`: Manually triggers background REM dream consolidation and outputs metrics.
  - `exit`, `quit`, `q`: Closes the terminal session.

### 4.2 `baby-llm serve`
Launches the local FastAPI REST API server and background daemons:
```bash
.venv/bin/python -m baby_llm.cli serve --host 127.0.0.1 --port 21225
```
- **CLI Options**:
  - `--host HOST`: Bind host interface (default: `127.0.0.1` or `BABY_LLM_API_HOST`).
  - `--port PORT`: Port number to bind (default: `21225` or `BABY_LLM_API_PORT`).
- **Background Lifecycle**: Automatically spins up background worker threads for `DreamWorker`, `VaultSyncManager`, and `PersonalSuccessAgent`.

### 4.3 `baby-llm ui`
Opens the default web browser to the running Glass-Box dashboard:
```bash
.venv/bin/python -m baby_llm.cli ui --port 21225
```

### 4.4 `baby-llm dream`
Executes an immediate one-shot REM Dream consolidation cycle headlessly:
```bash
.venv/bin/python -m baby_llm.cli dream
```

### 4.5 `baby-llm memories`
Prints all currently active facts from the bi-temporal knowledge graph:
```bash
.venv/bin/python -m baby_llm.cli memories
```

### 4.6 `baby-llm mcp`
Launches the Model Context Protocol (MCP) server over standard I/O (`stdio`).

---

## 5. Glass-Box Web Dashboard (`ui/`)

The Glass-Box Dashboard runs on **Port 21225** (`http://127.0.0.1:21225/`) and serves as the visual inspection window for human oversight.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      GLASS-BOX WEB DASHBOARD VIEWS                     │
├────────────────────┬───────────────────────────────────────────────────┤
│ View Panel         │ Capabilities & Operator Controls                  │
├────────────────────┼───────────────────────────────────────────────────┤
│ Mindstream         │ Real-time stream of extracted knowledge nodes     │
│ Memory Graph       │ Filter by category, view confidence & stability   │
│ Success Compass    │ Morning Brief, daily wins, active goals list      │
│ One-Click Erase    │ Delete any memory node permanently from disk      │
└────────────────────┴───────────────────────────────────────────────────┘
```

### Key UI Features:
1. **Mindstream Feed**: Displays memories as cards showing Subject-Predicate-Object structure, confidence badges, and YMYL encryption indicators.
2. **Category Filters**: Filter between `WORK`, `GOAL`, `PREFERENCE`, `HEALTH`, `FINANCE`, and `RELATIONSHIP`.
3. **One-Click Erase**: Allows humans to immediately delete any hallucinated or obsolete fact.
4. **Trigger Dream Button**: Allows manual invocation of the REM Dream cycle directly from the web interface.
5. **Standalone PWA**: Includes `manifest.json` and `icon.svg` for installation as a native desktop application.

---

## Next Steps
- Review system topology and lifecycles: **[architecture.md](architecture.md)**
- Study the fast-path engine and decay formulas: **[core-engine.md](core-engine.md)**
- Inspect storage schemas and encryption: **[configuration-and-storage.md](configuration-and-storage.md)**
