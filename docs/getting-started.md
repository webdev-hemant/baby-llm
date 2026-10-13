# 🚀 Getting Started with Baby LLM

*Prerequisites, Installation, Agent Quickstart, Operational Modes, and First-Run Verification*

---

## 1. System Requirements & Prerequisites

Baby LLM is engineered to run 100% offline on standard consumer hardware without requiring cloud accounts, external API keys, or specialized GPU clusters.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      MINIMUM SYSTEM REQUIREMENTS                       │
├───────────────────────┬────────────────────────────────────────────────┤
│ Component             │ Requirement                                    │
├───────────────────────┼────────────────────────────────────────────────┤
│ Python Runtime        │ Python 3.11 or higher (verified on 3.12.13)    │
│ Host Operating System │ macOS (ARM64/x86_64), Linux, or Windows (WSL2) │
│ Memory (RAM)          │ 2 GB minimum (4 GB recommended)                │
│ Disk Storage          │ ~1.5 GB for base venv, GGUF, & ONNX models     │
│ OS Credential Store   │ macOS Keychain, Linux Secret Service, WinCred  │
│ Inference Engine      │ Embedded Qwen2.5-0.5B GGUF (Zero-Daemon)       │
└───────────────────────┴────────────────────────────────────────────────┘
```

### 100% Self-Contained In-Process Inference:
- **Zero Daemon Required**: Baby LLM includes an embedded inference engine (`llama-cpp-python`) that automatically loads and runs `Qwen2.5-0.5B-Instruct-GGUF` (`qwen2.5-0.5b-instruct-q4_k_m.gguf` ~398 MB) locally. No background services, external daemons, or Ollama required.

---

## 2. Installation Options

### Option A: One-Liner Installer (Recommended for macOS & Linux)
Install Baby LLM and all embedded runtime dependencies without manual virtual environment management:
```bash
curl -fsSL https://raw.githubusercontent.com/webdev-hemant/baby-llm/main/install.sh | bash
```

### Option B: Step-by-Step Manual Installation
For developers and contributors who want to inspect or modify the source:

#### Step 2.1: Clone the Repository
Open a terminal and clone the repository:
```bash
git clone https://github.com/webdev-hemant/baby-llm.git
cd baby-llm
```

### Step 2.2: Create and Activate a Virtual Environment
Using `uv` (recommended for ultra-fast package resolution):
```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
```

Alternatively, using standard Python `venv`:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
*(On Windows PowerShell, use `.\.venv\Scripts\Activate.ps1`)*

### Step 2.3: Install Baby LLM in Editable Mode
Install the package and all runtime dependencies:
```bash
# Using uv:
uv pip install -e .

# Using standard pip:
pip install -e .
```

### Step 2.4: Verify the Installation
Check that the console script entry point is registered and functional:
```bash
baby-llm --help
```
You can also invoke the module directly using Python:
```bash
.venv/bin/python -m baby_llm.cli --help
```

Expected output:
```text
usage: baby-llm [-h] {chat,dream,memories,mcp,ui,serve} ...

Baby LLM Companion CLI

positional arguments:
  {chat,dream,memories,mcp,ui,serve}
    chat                Start interactive chat
    dream               Trigger REM dream consolidation cycle
    memories            List active memory nodes
    mcp                 Run Universal MCP server over stdio
    ui                  Open Glass-box UI in default web browser
    serve               Run FastAPI local REST server
```

---

## 3. Autonomous Agent Quickstart (Cursor, Claude & Python)

Connect Baby LLM as a persistent long-term memory tool for your AI agents in under 60 seconds:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   UNIVERSAL MCP SERVER ARCHITECTURE                    │
└────────────────────────────────────────────────────────────────────────┘

 [Cursor IDE / Claude Desktop / Agent Swarm]
               │
               ▼ (stdio JSON-RPC protocol)
┌────────────────────────────────────────────────────────────────────────┐
│ baby-llm mcp (FastMCP Server)                                          │
│   ├─ recall_memory(query, top_k)                                       │
│   ├─ commit_fact(subject, predicate, object, category, ymyl)           │
│   ├─ get_active_goals()                                                │
│   └─ record_daily_win(note)                                            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
 [Local SQLite Bi-Temporal Graph & LanceDB Vector Store (~/.baby_llm/)]
```

### 3.1 Configure Cursor IDE
1. Open Cursor Settings (`Cmd + ,` or `Ctrl + ,`).
2. Navigate to **Features** -> **MCP**.
3. Click **+ Add New MCP Server**.
4. Configure the server parameters:
   - **Name**: `baby-llm`
   - **Type**: `command`
   - **Command**: `/path/to/baby-llm/.venv/bin/python -m baby_llm.cli mcp`
5. Click **Save** and verify the green status indicator.

### 3.2 Configure Claude Desktop
Open or create your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the `baby-llm` entry:
```json
{
  "mcpServers": {
    "baby-llm": {
      "command": "/path/to/baby-llm/.venv/bin/python",
      "args": ["-m", "baby_llm.cli", "mcp"]
    }
  }
}
```

### 3.3 Quick Python Agent Test Script
Verify memory recall and commitment programmatically:
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="/path/to/baby-llm/.venv/bin/python",
    args=["-m", "baby_llm.cli", "mcp"],
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Commit a project decision
            await session.call_tool("commit_fact", {
                "subject": "project_phoenix",
                "predicate": "uses",
                "object_": "sqlite_lancedb",
                "category": "work"
            })
            
            # 2. Recall the memory in <30ms
            result = await session.call_tool("recall_memory", {"query": "project phoenix database"})
            print("Recalled:", result.content[0].text)

asyncio.run(main())
```

---

## 4. The 5 Operational Launch Modes

Baby LLM provides five distinct operational modes tailored to agent backends, human chat, and developer maintenance:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     THE 5 OPERATIONAL LAUNCH MODES                     │
├─────────────────┬──────────────────────────────────────────────────────┤
│ Command         │ Operational Scope & Behavior                         │
├─────────────────┼──────────────────────────────────────────────────────┤
│ baby-llm mcp    │ Model Context Protocol stdio server for AI agents    │
│ baby-llm serve  │ FastAPI REST server + Glass-Box UI on port 21225     │
│ baby-llm chat   │ Interactive terminal companion (<30ms fast-path)     │
│ baby-llm ui     │ Opens browser directly to http://127.0.0.1:21225/    │
│ baby-llm dream  │ Headless REM dream memory consolidation trigger      │
└─────────────────┴──────────────────────────────────────────────────────┘
```

### Mode 1: Universal MCP Server for Agents
Launches the stdio JSON-RPC server used by Cursor IDE and Claude Desktop:
```bash
.venv/bin/python -m baby_llm.cli mcp
```

### Mode 2: Launch FastAPI Server & Glass-Box Dashboard
Start the local REST server and background daemons:
```bash
.venv/bin/python -m baby_llm.cli serve
```
By default, the server binds to `127.0.0.1:21225`.

> [!NOTE]
> **Why Port 21225?**
> - **Mnemonic Encoding**: `21225` spells **`B-A-B-Y`** (`B=2, A=1, B=2, Y=25`).
> - **Collision Avoidance**: Situated in the user-registered port range (`1024`–`49151`), it prevents conflicts with Vite (`5173`), Next.js (`3000`), FastAPI/Django (`8000`), and PostgreSQL (`5432`).

### Mode 3: Interactive Terminal Chat
Chat directly with Baby LLM from your shell:
```bash
.venv/bin/python -m baby_llm.cli chat
```
*Special Commands during chat:*
- `/dream`: Manually triggers a REM Dream consolidation cycle right in your terminal.
- `exit` or `quit`: Gracefully closes the session.

### Mode 4: Open the Web UI Dashboard
In a separate terminal (while `serve` is running), launch the Glass-Box dashboard:
```bash
.venv/bin/python -m baby_llm.cli ui
```
This opens `http://127.0.0.1:21225/` in your default browser.

### Mode 5: Headless REM Dream Consolidation
Trigger a one-shot background consolidation cycle without opening a chat session:
```bash
.venv/bin/python -m baby_llm.cli dream
```
This processes unflagged interaction logs, extracts atomic facts, resolves contradictions, and updates vector indices.

---

## 5. End-to-End First-Run Walkthrough

Follow this step-by-step walkthrough to witness how Baby LLM absorbs context, recalls facts in real time, and resolves updates.

### Step 1: Launch Interactive Chat
```bash
.venv/bin/python -m baby_llm.cli chat
```

### Step 2: Introduce Personal Facts
Type the following statement:
```text
You > I am relocating from Seattle to Austin next month, and my goal is to launch Project Phoenix.
```

**What happens behind the scenes:**
1. The **Context Assembler** injects your base persona and recent conversation turns into working memory (<2ms).
2. The **Hybrid Retriever** queries SQLite FTS5 and LanceDB (<15ms).
3. The **Unified LLM Provider** synthesizes a response via embedded Qwen2.5-0.5B.
4. The **Write-Ahead Log (WAL)** immediately appends the raw turn to SQLite (`interaction_log`) without blocking.
5. The **Gentle Curiosity Protocol** detects an ambiguous project entity (`Project Phoenix`) and appends a gentle probe:
   ```text
   Baby LLM > Congratulations on the upcoming move to Austin! Launching Project Phoenix will be an exciting chapter.
   
   💭 By the way, you mentioned Project Phoenix—is this an internal initiative or a client milestone?
   ```

### Step 3: Trigger Memory Consolidation
Type the `/dream` command directly in the chat session:
```text
You > /dream
```
Output:
```text
🌙 Running REM Dream Consolidation...
Dream Complete: {'turns_processed': 1, 'facts_extracted': 2, 'nodes_archived': 0, 'active_nodes_count': 2}
```

### Step 4: Verify Memory Extraction
Exit the chat (`exit`) and inspect the knowledge graph:
```bash
.venv/bin/python -m baby_llm.cli memories
```
Output:
```text
🧠 Baby LLM Active Memories (2 facts):
------------------------------------------------------------
• [LIFESTYLE] user lives_in Austin
  Confidence: 95% | Stability: 1.0 | ID: a1b2c3d4
• [GOAL] user goal_is launch Project Phoenix
  Confidence: 95% | Stability: 1.0 | ID: e5f6a7b8
------------------------------------------------------------
```

### Step 5: Test Real-Time Recall
Restart chat:
```bash
.venv/bin/python -m baby_llm.cli chat
```
Ask:
```text
You > Where do I live and what should I focus on?
```
Baby LLM immediately recalls your home in Austin and your objective for Project Phoenix, citing your personal context without cloud latency.

---

## 6. Initial Configuration & Environment Setup

Baby LLM works immediately out of the box with zero configuration. All state is preserved in your home directory under `~/.baby_llm/`.

To customize behavior, create a `.env` file in the project root:
```bash
cp .env.example .env
```

Key environment configuration variables:
```bash
# Storage directory (default: ~/.baby_llm)
# BABY_LLM_APP_DIR=~/.baby_llm

# REST API Server host and port
BABY_LLM_API_HOST=127.0.0.1
BABY_LLM_API_PORT=21225

# Embedded Local Inference Engine (Zero Daemon / Zero Ollama)
BABY_LLM_EMBEDDED_MODEL_REPO=Qwen/Qwen2.5-0.5B-Instruct-GGUF
BABY_LLM_EMBEDDED_MODEL_FILENAME=qwen2.5-0.5b-instruct-q4_k_m.gguf

# Episodic Ring Buffer size (default: 15 turns)
BABY_LLM_RING_BUFFER_SIZE=15

# REM Dream idle trigger threshold in seconds (default: 900 = 15m)
BABY_LLM_IDLE_TRIGGER_SECONDS=900
```

For the complete list of settings and storage options, consult [configuration-and-storage.md](configuration-and-storage.md).

---

## 7. Common First-Run Pitfalls & Troubleshooting

### 1. First-Run Model Download Latency
- **Symptom**: On the very first `chat` execution, the terminal pauses for 10–30 seconds before responding.
- **Cause**: The embedded engine downloads the 398 MB `Qwen2.5-0.5B-Instruct-GGUF` model from Hugging Face, and FastEmbed downloads the 130 MB `bge-small-en-v1.5` ONNX model.
- **Resolution**: Subsequent runs use the local cache (`~/.cache/huggingface/` and `~/.cache/fastembed/`) and initialize in under 200 milliseconds.

### 2. Port 21225 Conflict
- **Symptom**: `ERROR: [Errno 48] Address already in use`.
- **Diagnosis**: Check if another instance of Baby LLM is already running:
  ```bash
  lsof -i :21225
  ```
- **Resolution**: Kill the existing process or launch with a custom port:
  ```bash
  baby-llm serve --port 21226
  ```

### 3. Headless / SSH Environment (OS Keyring Fallback)
- **Symptom**: `OS Keyring retrieval failed or unavailable`.
- **Behavior**: Baby LLM automatically falls back to an air-gapped local key file at `~/.baby_llm/.ymyl_key` with strict `0600` file permissions. No manual intervention is required.

---

## Next Steps
- Learn about the internal cognitive architecture: **[architecture.md](architecture.md)**
- Explore the fast-path engine and decay formulas: **[core-engine.md](core-engine.md)**
- Inspect REST APIs and MCP integration: **[interfaces-and-api.md](interfaces-and-api.md)**
