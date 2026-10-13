# 🛠️ Development, Testing & Extension Guide

*Local Environment Setup, 39-Test Pytest Suite, Mocking Strategies, Troubleshooting, and Extension Points*

---

## 1. Local Development Environment

Baby LLM is built with modern Python 3.11+ tooling and uses `hatchling` as its build backend (`pyproject.toml`).

### 1.1 Setting Up the Development Environment
```bash
# 1. Clone the repository
git clone https://github.com/webdev-hemant/baby-llm.git
cd baby-llm

# 2. Create Python 3.12 virtual environment using uv
uv venv --python 3.12 .venv
source .venv/bin/activate

# 3. Install in editable mode with all dependencies
uv pip install -e .
```

### 1.2 Development Tooling
- **Test Runner**: `pytest>=8.0.0` with `pytest-asyncio>=0.23.0`
- **Type Checking & Data Validation**: `pydantic>=2.6.0` and `pydantic-settings>=2.2.0`
- **Web & API Framework**: `fastapi>=0.110.0` and `uvicorn>=0.28.0`
- **Storage Engines**: Embedded `sqlite3`, `lancedb>=0.6.0`, and `pyarrow>=15.0.0`
- **Embeddings & Inference**: `fastembed>=0.2.7`, `llama-cpp-python>=0.2.70`, `huggingface-hub>=0.23.0`
- **Protocol & Filesystem**: `mcp>=1.0.0,<2.0.0`, `watchdog>=4.0.0`, `pyyaml>=6.0.0`

---

## 2. Comprehensive Test Suite & Verification

Baby LLM maintains a rigorous automated test suite consisting of **39 passing test cases** across unit and integration tiers.

```text
┌────────────────────────────────────────────────────────────────────────┐
│           AUTOMATED TEST SUITE BREAKDOWN (39 PASSING TESTS)            │
├────────────────────────┬───────┬─────────────┬─────────────────────────┤
│ Test Suite File        │ Tests │ Category    │ Verified Subsystems     │
├────────────────────────┼───────┼─────────────┼─────────────────────────┤
│ test_wal.py            │ 3     │ Unit        │ Append, fetch, & mark   │
│ test_graph_store.py    │ 3     │ Unit        │ Bi-temporal CRUD & hist │
│ test_decay.py          │ 3     │ Unit        │ Ebbinghaus math & YMYL  │
│ test_encryption.py     │ 4     │ Unit        │ AES-GCM-256 & Keyring   │
│ test_hybrid_retrieval  │ 2     │ Unit        │ BM25, LanceDB, and RRF  │
│ test_curiosity.py      │ 2     │ Unit        │ Probe limit & reset     │
│ test_tracker.py        │ 1     │ Unit        │ Commitments tracking    │
│ test_vault_sync.py     │ 3     │ Unit        │ Markdown export/import  │
│ test_cli.py            │ 3     │ Unit        │ CLI subparsers: ui, mem │
│ test_success_agent.py  │ 4     │ Unit        │ Briefs & scheduler      │
│ test_dream_cycle.py    │ 2     │ Integration │ End-to-end REM & daemon │
│ test_api_server.py     │ 7     │ Integration │ FastAPI endpoints & WAL │
│ test_mcp_server.py     │ 2     │ Integration │ FastMCP tools lifecycle │
└────────────────────────┴───────┴─────────────┴─────────────────────────┘
```

### 2.1 Running Tests
Execute the entire test suite from the repository root:
```bash
.venv/bin/pytest -v
```

Execute a specific unit test module:
```bash
.venv/bin/pytest tests/unit/test_graph_store.py -v
```

Execute integration tests only:
```bash
.venv/bin/pytest tests/integration/ -v
```

---

## 3. Test Suites Catalog & Verifications

### 3.1 Unit Test Suites (`tests/unit/`)
1. **`test_wal.py` (3 tests)**:
   - `test_append_and_retrieve_turn`: Confirms non-blocking turn insertion into `interaction_log`.
   - `test_append_and_retrieve_unprocessed_turns`: Validates chronological filtering where `processed_in_dream = 0`.
   - `test_mark_turns_processed`: Confirms atomic status updates after consolidation.
2. **`test_graph_store.py` (3 tests)**:
   - `test_insert_and_active_lookup`: Validates active node indexing and retrieval.
   - `test_bi_temporal_invalidation_and_history`: Validates contradiction handling, verifying that old facts are archived with `invalid_from` while new facts are committed with `valid_from = now`.
   - `test_reinforce_node`: Confirms stability doubling upon active retrieval.
3. **`test_decay.py` (3 tests)**:
   - `test_ymyl_retention_floor`: Verifies that health and finance facts maintain permanent $R(t) = 1.0$ retention.
   - `test_ebbinghaus_decay_curve`: Validates mathematical exponential decay over elapsed days.
   - `test_stability_extension`: Verifies that higher stability values significantly extend retention half-lives.
4. **`test_encryption.py` (4 tests)**:
   - `test_encryption_manager_roundtrip`: Verifies AES-GCM-256 encryption and decryption roundtrips.
   - `test_decryption_idempotency_and_unencrypted`: Confirms that unencrypted plaintext strings pass through unchanged.
   - `test_tampered_ciphertext_fails`: Asserts authentication failure on corrupted ciphertexts.
   - `test_graph_store_ymyl_at_rest_encryption`: Confirms that YMYL objects are encrypted in SQLite tables at rest.
5. **`test_hybrid_retrieval.py` (2 tests)**:
   - `test_bm25_exact_match`: Verifies SQLite FTS5 exact keyword matching.
   - `test_hybrid_retrieval_rrf`: Verifies Reciprocal Rank Fusion calculation combining BM25 and dense vector cosine distances.
6. **`test_curiosity.py` (2 tests)**:
   - `test_gentle_curiosity_probe_detection`: Tests regex detection of named projects (`project <name>`).
   - `test_gentle_curiosity_session_reset`: Confirms session boundaries and the strict 1-probe-per-session ceiling.
7. **`test_tracker.py` (1 test)**:
   - `test_commitment_lifecycle`: Tests transitions across `pending`, `in_progress`, `completed`, and `dropped`.
8. **`test_vault_sync.py` (3 tests)**:
   - `test_vault_markdown_export_and_frontmatter`: Verifies YAML frontmatter generation.
   - `test_vault_markdown_import`: Confirms parsing and graph reconciliation from modified Markdown files.
   - `test_vault_watchdog_observer_lifecycle`: Tests starting and stopping the filesystem observer daemon.
9. **`test_cli.py` (3 tests)**:
   - `test_cli_subparser_ui`: Tests the `ui` subparser arguments (`--port`, `--host`).
   - `test_cli_subparser_memories`: Verifies active memory formatting in the CLI.
   - `test_cli_subparser_dream`: Confirms dream command execution.
10. **`test_success_agent.py` (4 tests)**:
    - `test_morning_brief_and_daily_caching`: Verifies 07:30 Morning Brief synthesis and SQLite daily caching.
    - `test_overdue_commitments_watchdog`: Verifies overdue deadline alerts.
    - `test_evening_reflection`: Tests evening reflection generation.
    - `test_autonomous_scheduler_lifecycle`: Confirms start/stop lifecycle of the scheduler thread.

### 3.2 Integration Test Suites (`tests/integration/`)
1. **`test_dream_cycle.py` (2 tests)**:
   - `test_full_dream_consolidation_and_contradiction`: End-to-end integration test spanning dialogue ingestion, atomic SPO triple extraction, contradiction resolution, and vector store updates.
   - `test_dream_worker_background_daemon`: Verifies autonomous background worker execution, idle timeout triggers, and user activity pause/resume mechanics.
2. **`test_api_server.py` (7 tests)**:
   - `test_root_serves_html`: Tests root route serving dashboard HTML.
   - `test_health_check`: Verifies `GET /api/health`.
   - `test_memory_lifecycle_api`: Validates full REST lifecycle (create, list, delete).
   - `test_success_compass_api`: Verifies `GET /api/success/compass`.
   - `test_manifest_endpoint`: Validates PWA `manifest.json`.
   - `test_memory_update_api`: Tests in-place memory update via `PUT /api/memories/{id}`.
   - `test_chat_incognito_bypasses_wal`: Verifies that incognito chat turns completely bypass WAL logging.
3. **`test_mcp_server.py` (2 tests)**:
   - `test_mcp_commit_fact_and_recall`: Validates `commit_fact` and `recall_memory` MCP tools.
   - `test_mcp_goals_and_daily_win`: Validates `get_active_goals` and `record_daily_win` MCP tools.

---

## 4. Test Isolation & Mocking Strategies

To ensure reliable, deterministic test execution:
- **`tmp_path` Fixtures**: Unit tests inject temporary directories (`tmp_path / "test.sqlite3"`, `tmp_path / "lancedb_test"`) to avoid polluting the operator's real `~/.baby_llm` database.
- **Fast Mock Extractors**: Tests that validate daemon orchestration use lightweight mock extractors (`FastMockExtractor`) to bypass neural network forward passes.
- **In-Memory Starlette TestClient**: FastAPI REST endpoints are tested via `fastapi.testclient.TestClient`, executing HTTP requests directly in-process without network overhead.

---

## 5. Diagnostic & Troubleshooting Matrix

```text
┌────────────────────────────────────────────────────────────────────────┐
│                  DIAGNOSTIC & TROUBLESHOOTING MATRIX                   │
├──────────────────────┬────────────────────────┬────────────────────────┤
│ Observed Symptom     │ Root Cause             │ Resolution Command     │
├──────────────────────┼────────────────────────┼────────────────────────┤
│ Database is locked   │ Lock acquire timeout   │ Verify WAL pragma mode │
│ Port 21225 in use    │ Another server running │ Use --port <custom>    │
│ Keyring unavailable  │ Headless / CI server   │ Fallback to keyfile    │
│ First run chat lag   │ Initial GGUF download  │ Cached for future runs │
│ FTS5 syntax error    │ Unsanitized user query │ BM25 tokenizer cleans  │
└──────────────────────┴────────────────────────┴────────────────────────┘
```

### Deep-Dive Troubleshooting Solutions:
1. **SQLite `OperationalError: database is locked`**:
   - Verify that all database connections are acquired through `db_manager.get_connection()`, which guarantees context management and automatic rollback on errors.
   - Confirm WAL mode is active:
     ```bash
     sqlite3 ~/.baby_llm/baby_llm.sqlite3 "PRAGMA journal_mode;"
     # Should return: wal
     ```
2. **Port 21225 Already Bound**:
   - Check which PID holds the port:
     ```bash
     lsof -i :21225
     ```
   - Kill the orphan process or launch on a different port:
     ```bash
     baby-llm serve --port 21226
     ```
3. **Headless / Containerized Environments**:
   - When running in Docker or over SSH where an OS desktop keyring (D-Bus / Secret Service) is absent, Baby LLM gracefully writes a 256-bit AES master key to `~/.baby_llm/.ymyl_key` with permissions `0600`.

---

## 6. Extending Baby LLM

Baby LLM is designed with modular extension points:

### 6.1 Adding a New Memory Category
To introduce a new memory category (e.g. `academic`):
1. **Update `models.py`**:
   ```python
   class MemoryCategory(str, Enum):
       ...
       ACADEMIC = "academic"
   ```
2. **Update SQLite CHECK Constraint in `db.py`**:
   Add `'academic'` to the `category IN (...)` check constraint in `SCHEMA_SQL`.
3. **Define Importance Weight in `decay.py`**:
   ```python
   weights = {
       ...
       "academic": 2.2,
   }
   ```
4. **Add CSS Styling in `ui/styles.css`**:
   ```css
   .category-tag.academic {
       background: rgba(147, 51, 234, 0.15);
       color: #c084fc;
       border-color: rgba(147, 51, 234, 0.3);
   }
   ```

### 6.2 Adding a Custom Local LLM Backend
To integrate a custom local model provider (e.g. vLLM or llamafile):
1. Open `src/baby_llm/runtime/llm_provider.py`.
2. Add your custom client invocation inside `UnifiedLLMProvider.chat_sync()`.
3. Maintain the standard messages payload: `[{"role": "system", "content": ...}, {"role": "user", ...}]`.

### 6.3 Adding New Model Context Protocol (MCP) Tools
To expose a new capability to Claude Desktop or Cursor:
1. Open `src/baby_llm/mcp/server.py`.
2. Decorate your function with `@mcp.tool()`:
   ```python
   @mcp.tool()
   def list_top_priorities() -> str:
       """Surfaces the user's top needle-moving goals for today."""
       commitments = success_tracker.get_active_commitments()
       return "\n".join(f"- {c.title}" for c in commitments[:3])
   ```
3. Restart your Claude Desktop or Cursor MCP session.

---

## Next Steps
- Review architecture and component topology: **[architecture.md](architecture.md)**
- Review fast-path context assembly and decay curves: **[core-engine.md](core-engine.md)**
- Review configuration options and database schemas: **[configuration-and-storage.md](configuration-and-storage.md)**
- Review CLI commands and REST APIs: **[interfaces-and-api.md](interfaces-and-api.md)**
