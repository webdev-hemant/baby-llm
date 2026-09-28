"""Bidirectional Markdown & Obsidian Vault synchronization."""

import os
from pathlib import Path
from typing import Optional
import yaml
from baby_llm.config import settings
from baby_llm.core.models import MemoryCategory, MemoryNode
from baby_llm.dream.resolver import conflict_resolver
from baby_llm.storage.graph_store import BiTemporalGraphStore, graph_store
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
from watchdog.observers import Observer


class VaultSyncManager:
    def __init__(
        self,
        vault_path: Path = settings.vault_path,
        graph: BiTemporalGraphStore = graph_store,
    ):
        self.vault_path = vault_path
        self.memories_folder = vault_path / "memories"
        self.graph = graph
        self._observer: Optional[Observer] = None

    def export_all_memories(self) -> int:
        """Export all active memory nodes as markdown files with front-matter."""
        self.memories_folder.mkdir(parents=True, exist_ok=True)
        nodes = self.graph.get_active_nodes()
        for node in nodes:
            self._write_node_to_markdown(node)
        return len(nodes)

    def _write_node_to_markdown(self, node: MemoryNode) -> Path:
        file_path = self.memories_folder / f"{node.id}.md"
        front_matter = {
            "id": node.id,
            "subject": node.subject,
            "predicate": node.predicate,
            "object": node.object,
            "category": node.category.value,
            "confidence": node.confidence,
            "ymyl_protected": node.ymyl_protected,
            "valid_from": node.valid_from.isoformat(),
        }
        content = (
            f"---\n{yaml.dump(front_matter, sort_keys=False)}---\n\n"
            f"# {node.to_readable_fact()}\n\n"
            f"*Stored by Baby LLM in the Bi-Temporal Memory Graph.*"
        )
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def import_from_markdown(self, file_path: Path) -> Optional[MemoryNode]:
        """Parse markdown file and commit updates to graph."""
        if not file_path.name.endswith(".md"):
            return None

        content = file_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return None

        try:
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None
            meta = yaml.safe_load(parts[1])
            if not isinstance(meta, dict) or "subject" not in meta:
                return None

            return conflict_resolver.resolve_and_commit(
                subject=meta["subject"],
                predicate=meta["predicate"],
                object_=meta["object"],
                category=MemoryCategory(meta.get("category", "preference")),
                confidence=float(meta.get("confidence", 1.0)),
                ymyl_protected=bool(meta.get("ymyl_protected", False)),
            )
        except Exception:
            return None


class VaultWatchdogHandler(FileSystemEventHandler):
    def __init__(self, sync_manager: VaultSyncManager):
        self.sync_manager = sync_manager

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            self.sync_manager.import_from_markdown(Path(event.src_path))

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            self.sync_manager.import_from_markdown(Path(event.src_path))


vault_sync = VaultSyncManager()
