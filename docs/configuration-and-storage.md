# ⚙️ Configuration & Storage Architecture

*Environment Variables, Settings Management, SQLite Schemas & FTS5, LanceDB Vector Tables, AES-GCM-256 Encryption, and Obsidian Sync*

---

## 1. Configuration Management (`Settings`)

Baby LLM centralizes configuration management in `src/baby_llm/config.py` using Pydantic Settings (`pydantic-settings`).

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                       CONFIGURATION SETTINGS REFERENCE (BABY_LLM_*)                    │
├────────────────────────┬────────────────────────────────────┬──────────────────────────┤
│ Setting Field          │ Default Value                      │ Description & Role       │
├────────────────────────┼────────────────────────────────────┼──────────────────────────┤
│ app_dir                │ ~/.baby_llm                        │ Root data storage path   │
│ db_filename            │ baby_llm.sqlite3                   │ SQLite database file     │
│ lancedb_dirname        │ lancedb                            │ LanceDB vector folder    │
│ vault_dirname          │ vault                              │ Obsidian sync folder     │
│ api_host               │ 127.0.0.1                          │ FastAPI host binding     │
│ api_port               │ 21225                              │ FastAPI port (B-A-B-Y)   │
│ embedded_model_repo    │ Qwen/Qwen2.5-0.5B-Instruct-GGUF    │ HF model repository      │
│ embedded_model_filename│ qwen2.5-0.5b-instruct-q4_k_m.gguf  │ Embedded GGUF model file │
│ embedded_model_n_ctx   │ 2048                               │ Context window size      │
│ embedding_model        │ BAAI/bge-small-en-v1.5             │ FastEmbed ONNX model     │
│ embedding_dimension    │ 384                                │ Embedding vector size    │
│ idle_trigger_seconds   │ 900                                │ Inactivity timeout 15m   │
│ dream_cron_hour        │ 3                                  │ Nightly 03:00 cron hr    │
│ ring_buffer_size       │ 15                                 │ Episodic ring turns      │
│ hybrid_top_k           │ 5                                  │ Retrieved facts count    │
│ rrf_k_constant         │ 60                                 │ RRF smoothing factor     │
└────────────────────────┴────────────────────────────────────┴──────────────────────────┘
```

### 1.1 Environment Variable Precedence
All configuration fields support overriding via:
1. Environment variables prefixed with `BABY_LLM_` (e.g. `export BABY_LLM_API_PORT=21225`).
2. A local `.env` file situated in the application working directory.
3. Codebase defaults declared in `Settings()`.

### 1.2 Production `.env.example` Template
```bash
# ==============================================================================
# Baby LLM Configuration File (.env)
# ==============================================================================

# Storage Paths
# BABY_LLM_APP_DIR=~/.baby_llm
BABY_LLM_DB_FILENAME=baby_llm.sqlite3
BABY_LLM_LANCEDB_DIRNAME=lancedb
BABY_LLM_VAULT_DIRNAME=vault

# Local REST Server
BABY_LLM_API_HOST=127.0.0.1
BABY_LLM_API_PORT=21225

# Embedded Local Inference Engine (Zero Daemon / Zero Ollama)
BABY_LLM_EMBEDDED_MODEL_REPO=Qwen/Qwen2.5-0.5B-Instruct-GGUF
BABY_LLM_EMBEDDED_MODEL_FILENAME=qwen2.5-0.5b-instruct-q4_k_m.gguf
BABY_LLM_EMBEDDED_MODEL_N_CTX=2048
BABY_LLM_EMBEDDED_MODEL_N_THREADS=4

# Embeddings & Hybrid Retrieval
BABY_LLM_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
BABY_LLM_EMBEDDING_DIMENSION=384
BABY_LLM_HYBRID_TOP_K=5
BABY_LLM_RRF_K_CONSTANT=60

# Context & Memory Buffers
BABY_LLM_RING_BUFFER_SIZE=15
BABY_LLM_IDLE_TRIGGER_SECONDS=900
BABY_LLM_DREAM_CRON_HOUR=3

# Success Agent Routine Timers
BABY_LLM_MORNING_BRIEF_HOUR=7
BABY_LLM_MORNING_BRIEF_MINUTE=30
BABY_LLM_EVENING_REFLECT_HOUR=21
BABY_LLM_EVENING_REFLECT_MINUTE=30
```

---

## 2. Storage Layout & Subsystem Mapping

Baby LLM maintains an air-gapped, sovereign storage directory structure inside `~/.baby_llm/`:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                  STORAGE LAYOUT & PERSISTENCE SCHEMAS                  │
├───────────────────┬────────────────────────┬───────────────────────────┤
│ Storage Layer     │ File / Table Path      │ Format & Purpose          │
├───────────────────┼────────────────────────┼───────────────────────────┤
│ SQLite WAL Table  │ interaction_log        │ Raw turns & timestamps    │
│ Bi-Temporal Graph │ memory_nodes           │ SPO facts with validity   │
│ FTS5 Full-Text    │ memory_fts             │ BM25 virtual index        │
│ LanceDB Vectors   │ lancedb/memories       │ 384-dim dense vectors     │
│ OS Keyring / File │ .ymyl_key (mode 0600)  │ AES-GCM-256 master key    │
│ Obsidian Mirror   │ vault/memories/*.md    │ YAML frontmatter notes    │
└───────────────────┴────────────────────────┴───────────────────────────┘
```

```text
~/.baby_llm/
├── baby_llm.sqlite3          # Primary SQLite database (WAL mode)
├── baby_llm.sqlite3-wal      # Active SQLite Write-Ahead Log journal
├── baby_llm.sqlite3-shm      # SQLite shared-memory index
├── .ymyl_key                 # Fallback AES-GCM-256 master key (mode 0600)
├── lancedb/                  # LanceDB columnar vector storage directory
│   └── memories.lance/       # FastEmbed 384-dim dense vector table
└── vault/                    # Obsidian Markdown mirror directory
    └── memories/             # Individual <node_id>.md files
```

---

## 3. SQLite Database Architecture (`DatabaseManager`)

Database connections are managed by `src/baby_llm/storage/db.py`.

### 3.1 Connection Pragmas & Concurrency
Every connection created via `db_manager.get_connection()` applies three critical performance pragmas:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
```
- **WAL Journal Mode**: Enables concurrent read operations (FastAPI and CLI queries) without being blocked by WAL writes or dream consolidation updates.
- **Normal Synchronous**: Balances atomic durability with fast SSD write performance.
- **Connection Timeout**: Set to 30.0 seconds to eliminate transient database lock exceptions.

### 3.2 Complete SQLite Table Schemas

#### 1. Write-Ahead Interaction Log (`interaction_log`)
Captures raw conversational turns in real time without blocking the chat path:
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

#### 2. Bi-Temporal Memory Nodes (`memory_nodes`)
Stores atomic Subject-Predicate-Object triples with bi-temporal validity markers:
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
    invalid_from TIMESTAMP,
    ymyl_protected BOOLEAN DEFAULT 0,
    source_turn_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_memory_active ON memory_nodes (invalid_from) WHERE invalid_from IS NULL;
CREATE INDEX IF NOT EXISTS idx_memory_category ON memory_nodes (category);
CREATE INDEX IF NOT EXISTS idx_memory_subject ON memory_nodes (subject);
```

#### 3. Full-Text Search Virtual Table (`memory_fts`) & Synchronization Triggers
Provides sub-5ms BM25 lexical searches synchronized with `memory_nodes`:
```sql
CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    node_id UNINDEXED,
    subject,
    predicate,
    object,
    category,
    tokenize = 'porter unicode61'
);

-- Trigger: Insert synchronization
CREATE TRIGGER IF NOT EXISTS trg_memory_nodes_ai AFTER INSERT ON memory_nodes BEGIN
    INSERT INTO memory_fts(node_id, subject, predicate, object, category)
    VALUES (new.id, new.subject, new.predicate, new.object, new.category);
END;

-- Trigger: Delete synchronization
CREATE TRIGGER IF NOT EXISTS trg_memory_nodes_ad AFTER DELETE ON memory_nodes BEGIN
    DELETE FROM memory_fts WHERE node_id = old.id;
END;

-- Trigger: Update synchronization
CREATE TRIGGER IF NOT EXISTS trg_memory_nodes_au AFTER UPDATE ON memory_nodes BEGIN
    DELETE FROM memory_fts WHERE node_id = old.id;
    INSERT INTO memory_fts(node_id, subject, predicate, object, category)
    VALUES (new.id, new.subject, new.predicate, new.object, new.category);
END;
```

#### 4. Commitments & Goals Tracking (`commitments`)
Manages the user's commitments and target deadlines:
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
```

#### 5. Daily Summaries Cache (`daily_summaries`)
Caches morning intention briefs and nightly reflections by calendar date:
```sql
CREATE TABLE IF NOT EXISTS daily_summaries (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL UNIQUE,
    summary_type TEXT CHECK(summary_type IN ('morning_brief', 'evening_reflection')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. LanceDB Vector Storage Architecture (`LanceVectorStore`)

The vector storage layer (`src/baby_llm/storage/vector_store.py`) uses **LanceDB**, an embedded, disk-native columnar vector database that runs in-process without requiring a separate Docker service.

### 4.1 PyArrow Schema Definition
The `memories` table is defined using the following PyArrow schema:
```python
schema = pa.schema([
    pa.field("id", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), 384)),
    pa.field("text", pa.string()),
    pa.field("category", pa.string()),
    pa.field("is_active", pa.bool_()),
    pa.field("ymyl_protected", pa.bool_()),
])
```

### 4.2 Query Execution & Filtering
When `search_similar()` is called:
```python
query = self._table.search(query_vector).metric("cosine")
if active_only:
    query = query.where("is_active = true")
results = query.limit(top_k).to_list()
```
- **SIMD Cosine Acceleration**: LanceDB evaluates cosine distances directly against disk-backed columnar files.
- **State Filtering**: Filtering by `is_active = true` ensures that archived facts or invalidated prior beliefs never contaminate real-time context.

---

## 5. Security & At-Rest Encryption Architecture (`YMYLEncryptionManager`)

Baby LLM enforces attribute-level encryption for high-stakes **YMYL** (Your Money or Your Life: financial, medical) facts (`src/baby_llm/security/encryption.py`).

### 5.1 Cryptographic Specification
- **Cipher**: **AES-GCM-256** (Galois/Counter Mode with 256-bit keys).
- **Nonce**: 96-bit (12 bytes) cryptographically random nonce generated per encryption via `os.urandom(12)`.
- **Authentication Tag**: 128-bit (16 bytes) GCM authentication tag verifying ciphertext integrity.
- **Envelope Format**:
  ```text
  ENC::<base64( 12-byte Nonce + Ciphertext + 16-byte Tag )>
  ```

### 5.2 Three-Tier Key Hierarchy
```text
 1. OS Keyring (service='baby_llm', username='ymyl_master_key')
        │
        ▼ (if unavailable)
 2. Local Keyfile (~/.baby_llm/.ymyl_key with mode 0600)
        │
        ▼ (if absent)
 3. Generate 256-Bit Master Key (AESGCM.generate_key(256))
```
- **Transparent Execution**: During `graph_store.insert_node()`, if `node.ymyl_protected = True`, `node.object` is automatically encrypted before database insertion. On query reads (`_row_to_node()`), the object is decrypted seamlessly in RAM.

---

## 6. Bidirectional Obsidian Vault Synchronization (`VaultSyncManager`)

Baby LLM maintains a bidirectional bridge between structured database records and local Markdown files (`src/baby_llm/sync/obsidian_sync.py`).

### 6.1 Markdown Frontmatter Schema
Each active memory node is saved to `~/.baby_llm/vault/memories/<node_id>.md`:
```markdown
---
id: 4e91f1c2-39c4-498b-9685-5b4d9ef092d6
subject: user
predicate: lives_in
object: Austin
category: lifestyle
confidence: 0.95
ymyl_protected: false
valid_from: '2026-10-13T01:00:00+00:00'
---

# user lives_in Austin

*Stored by Baby LLM in the Bi-Temporal Memory Graph.*
```

### 6.2 Watchdog Filesystem Observer
- A `watchdog.observers.Observer` daemon monitors `~/.baby_llm/vault/memories/`.
- When a user modifies or adds a markdown note in Obsidian:
  1. The `VaultWatchdogHandler` parses the modified frontmatter.
  2. `conflict_resolver.resolve_and_commit()` evaluates the change.
  3. Contradictions or updates are reconciled in SQLite and LanceDB automatically.

---

## Next Steps
- Explore CLI commands, REST APIs, and MCP tools: **[interfaces-and-api.md](interfaces-and-api.md)**
- Review local pytest suite and troubleshooting: **[development-and-testing.md](development-and-testing.md)**
- Review core cognitive architecture: **[core-engine.md](core-engine.md)**
