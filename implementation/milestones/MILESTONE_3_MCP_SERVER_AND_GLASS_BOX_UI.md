# Milestone 3: Universal MCP Server & Glass-Box Dashboard
*Weeks 7 – 9 • Primary Objective: Model Context Protocol (MCP) & Glass-Box Transparency*

---

## 1. Executive Summary & Objective

The primary objective of **Milestone 3** is to provide seamless external tool connectivity and complete user transparency:
1. **Universal Model Context Protocol (MCP)**: Exposes Baby LLM tools (`recall_memory`, `commit_fact`, `get_active_goals`, `record_daily_win`) to external development environments including Claude Desktop, Cursor IDE, and Zed over stdio.
2. **Glass-Box Transparency**: Empowers the user to inspect every learned memory, observe confidence and stability scores, view the bi-temporal historical trajectory, and instantly edit or erase any node with a single click.
3. **Collision-Proof Local Web Bridge (Port 21225)**: Eliminates heavy Rust/Tauri compilation overhead by serving a sleek, zero-scroll web dashboard directly via FastAPI on dedicated port `21225` (spelling `BABY`: B=2, A=1, B=2, Y=25).
4. **PWA Standalone Mode**: Enables one-click installation to the macOS Dock or Windows Taskbar via web manifest.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GLASS-BOX & MCP INTEGRATION TOPOLOGY                     │
├──────────────────────────────────────────────┬──────────────────────────────┤
│ External MCP Clients (stdio JSON-RPC)        │ Web Dashboard & PWA (:21225) │
│ • Claude Desktop / Cursor IDE / Zed          │ • Browser / Dock Window      │
├──────────────────────────────────────────────┴──────────────────────────────┤
│ Unified FastAPI & MCP Runtime Bridge                                        │
│ • baby_llm.mcp.server (Universal Model Context Protocol)                    │
│ • baby_llm.api.server (REST & WebSocket Engine on Port 21225)               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Core Knowledge Graph (SQLite) & Vector Store (LanceDB)                      │
│ • recall_memory  • commit_fact  • get_active_goals  • erase_memory          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Layout & Module Map

| Module Path | Primary Symbols / Classes | Responsibility |
| :--- | :--- | :--- |
| [`src/baby_llm/mcp/server.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/mcp/server.py) | [`run_mcp_server()`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/mcp/server.py#L93), FastMCP tools | Exposes stdio MCP tools for Cursor & Claude |
| [`src/baby_llm/api/server.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/api/server.py) | FastAPI app, REST endpoints | Local HTTP server on port 21225 serving API and UI |
| [`ui/index.html`](file:///Users/admin/Desktop/corporate/projects/baby-llm/ui/index.html) | Single-page application markup | Mindstream, bi-temporal timeline, chat stage, and modals |
| [`ui/styles.css`](file:///Users/admin/Desktop/corporate/projects/baby-llm/ui/styles.css) | Custom CSS design system | 100vh zero-scroll layout, ambient dark glow theme |
| [`ui/app.js`](file:///Users/admin/Desktop/corporate/projects/baby-llm/ui/app.js) | Reactive JavaScript state engine | REST communications, memory filters, timeline renderer |
| [`ui/manifest.json`](file:///Users/admin/Desktop/corporate/projects/baby-llm/ui/manifest.json) | Web App Manifest | Standalone window configuration for OS Dock install |

---

## 3. Tool Specifications & REST API Schema

### 3.1 Universal Model Context Protocol (MCP) Tools
* **`recall_memory(query: str, top_k: int = 5) -> str`**:
  Executes sub-20ms hybrid retrieval and returns verified personal context strings.
* **`commit_fact(subject: str, predicate: str, object_: str, category: str, ymyl_protected: bool) -> str`**:
  Explicitly persists or updates a fact through bi-temporal conflict resolution.
* **`get_active_goals() -> str`**:
  Retrieves active commitments and upcoming deadlines.
* **`record_daily_win(note: str) -> str`**:
  Appends an accomplishment directly to the knowledge graph under the `goal` category.

### 3.2 FastAPI REST Endpoints (Port 21225)
* **`GET /api/health`**: Service liveness and version telemetry.
* **`POST /api/chat`**: Synchronous fast-path chat invocation (`message`, `session_id`).
* **`GET /api/memories`**: Retrieves all memory nodes with category and active filters.
* **`POST /api/memories`**: Manually overrides or inserts a memory node.
* **`DELETE /api/memories/{id}`**: Permanently erases a memory node from SQLite and LanceDB.
* **`POST /api/dream/trigger`**: Triggers a manual REM dream consolidation cycle.
* **`GET /api/success/compass`**: Returns the morning readiness brief and active commitments.

---

## 4. Implementation Tasks & Deliverables

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MILESTONE 3 IMPLEMENTATION CHECKLIST                     │
├──────┬─────────────────────────────────────────────────┬────────────────────┤
│ Item │ Task Description                                │ Verification       │
├──────┼─────────────────────────────────────────────────┼────────────────────┤
│ 3.1  │ Universal MCP server (FastMCP / stdio)          │ Cursor/Claude CLI  │
│ 3.2  │ Dedicated port 21225 FastAPI service            │ test_api_server.py │
│ 3.3  │ Mindstream card feed with category filters      │ UI functional test │
│ 3.4  │ Bi-temporal trajectory timeline view            │ UI timeline test   │
│ 3.5  │ One-click fact erase and manual override modal  │ API deletion test  │
│ 3.6  │ PWA manifest.json configuration                 │ Chrome PWA inspect │
│ 3.7  │ Incognito mode toggle & in-place fact editor    │ WAL bypass test    │
│ 3.8  │ Automated integration test for MCP tools        │ test_mcp_server.py │
└──────┴─────────────────────────────────────────────────┴────────────────────┘
```

---

## 5. Verification Gates & Automated Test Suites

### 5.1 Verification Gate
* **Gate G6 (MCP Client Compatibility)**: External clients (Cursor IDE, Claude Desktop, Zed) discover and invoke tools without schema errors.

### 5.2 Test Coverage
* [`tests/integration/test_api_server.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/integration/test_api_server.py):
  * `test_root_serves_html()`: Confirms static dashboard delivery.
  * `test_health_check()`: Verifies system health endpoint.
  * `test_memory_lifecycle_api()`: Validates creation, retrieval, and deletion of memory nodes.
  * `test_memory_update_api()`: Validates in-place PUT update of existing memory nodes.
  * `test_chat_incognito_bypasses_wal()`: Validates incognito chat execution bypassing SQLite WAL persistence.
  * `test_manifest_endpoint()`: Verifies PWA manifest.json delivery.
  * `test_success_compass_api()`: Verifies active commitment retrieval and morning brief.
* [`tests/integration/test_mcp_server.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/integration/test_mcp_server.py):
  * `test_mcp_commit_fact_and_recall()`: Verifies external MCP clients committing and retrieving personal facts.
  * `test_mcp_goals_and_daily_win()`: Verifies active goal tracking and accomplishment logging via MCP tools.

---

## 6. Current Implementation Status & Outstanding Work

* **Completed (100%)**:
  * Universal MCP server is implemented with FastMCP and stdio launcher in [`src/baby_llm/mcp/server.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/src/baby_llm/mcp/server.py) and passing automated contract tests.
  * FastAPI REST API runs on collision-proof port `21225`, supporting full CRUD, in-place PUT updates, and incognito mode.
  * Web Dashboard features Mindstream card filtering, bi-temporal timeline rendering, in-place node editing, incognito stealth toggle, and PWA standalone desktop installation ([`ui/manifest.json`](file:///Users/admin/Desktop/corporate/projects/baby-llm/ui/manifest.json)).
  * Full integration test suites ([`tests/integration/test_api_server.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/integration/test_api_server.py), [`tests/integration/test_mcp_server.py`](file:///Users/admin/Desktop/corporate/projects/baby-llm/tests/integration/test_mcp_server.py)) verified and passing (22/22 tests across project).
* **Remaining Action Items**:
  * None. Milestone 3 is 100% complete, verified, and ready for Milestone 4 Personal Success Agent & Ecosystem Sync.
