"""Unit tests for bidirectional Obsidian Markdown Vault synchronization."""

from pathlib import Path
import tempfile
import time
import yaml

from baby_llm.core.models import MemoryCategory, MemoryNode
from baby_llm.storage.db import DatabaseManager
from baby_llm.storage.graph_store import BiTemporalGraphStore
from baby_llm.sync.obsidian_sync import VaultSyncManager, VaultWatchdogHandler


def test_vault_markdown_export_and_frontmatter():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "vault"
        db_path = Path(tmpdir) / "test_sync.db"
        db = DatabaseManager(db_path=db_path)
        graph = BiTemporalGraphStore(db=db)

        # Insert active memory
        node = MemoryNode(
            subject="user",
            predicate="lives_in",
            object="Seattle",
            category=MemoryCategory.LIFESTYLE,
            confidence=0.95,
        )
        graph.insert_node(node)

        sync_mgr = VaultSyncManager(vault_path=vault_path, graph=graph)
        count = sync_mgr.export_all_memories()
        assert count == 1

        md_file = vault_path / "memories" / f"{node.id}.md"
        assert md_file.exists()

        content = md_file.read_text(encoding="utf-8")
        assert content.startswith("---")
        parts = content.split("---", 2)
        meta = yaml.safe_load(parts[1])

        assert meta["id"] == node.id
        assert meta["subject"] == "user"
        assert meta["predicate"] == "lives_in"
        assert meta["object"] == "Seattle"
        assert meta["category"] == "lifestyle"
        assert meta["confidence"] == 0.95
        assert "user lives_in Seattle" in content


def test_vault_markdown_import():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "vault"
        sync_mgr = VaultSyncManager(vault_path=vault_path)

        memories_folder = vault_path / "memories"
        memories_folder.mkdir(parents=True, exist_ok=True)
        md_file = memories_folder / "test_import.md"

        frontmatter = {
            "id": "11111111-2222-3333-4444-555555555555",
            "subject": "user",
            "predicate": "speaks_language",
            "object": "Japanese",
            "category": "lifestyle",
            "confidence": 0.99,
            "ymyl_protected": False,
        }
        md_file.write_text(
            f"---\n{yaml.dump(frontmatter)}---\n\n# user speaks Japanese\n",
            encoding="utf-8",
        )

        imported = sync_mgr.import_from_markdown(md_file)
        assert imported is not None
        assert imported.subject == "user"
        assert imported.predicate == "speaks_language"
        assert imported.object == "Japanese"


def test_vault_watchdog_observer_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "vault"
        sync_mgr = VaultSyncManager(vault_path=vault_path)

        assert sync_mgr.is_observer_running is False
        sync_mgr.start_observer()
        assert sync_mgr.is_observer_running is True

        # Calling start again is idempotent
        sync_mgr.start_observer()
        assert sync_mgr.is_observer_running is True

        sync_mgr.stop_observer()
        assert sync_mgr.is_observer_running is False
