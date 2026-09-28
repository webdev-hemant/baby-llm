"""LanceDB vector storage layer for dense semantic memory retrieval."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import lancedb
import pyarrow as pa
from baby_llm.config import settings
from baby_llm.core.models import MemoryNode


class LanceVectorStore:
    TABLE_NAME = "memories"

    def __init__(self, db_path: Path = settings.lancedb_path):
        self.db_path = db_path
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(str(self.db_path))
        self._table = None
        self._ensure_table()

    def _ensure_table(self) -> None:
        try:
            self._table = self.db.open_table(self.TABLE_NAME)
        except Exception:
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), settings.embedding_dimension)),
                pa.field("text", pa.string()),
                pa.field("category", pa.string()),
                pa.field("is_active", pa.bool_()),
                pa.field("ymyl_protected", pa.bool_()),
            ])
            self._table = self.db.create_table(self.TABLE_NAME, schema=schema, exist_ok=True)

    def upsert_node(self, node: MemoryNode, vector: List[float]) -> None:
        """Upsert or replace vector record for memory node."""
        data = [{
            "id": node.id,
            "vector": vector,
            "text": node.to_readable_fact(),
            "category": node.category.value,
            "is_active": node.is_active,
            "ymyl_protected": node.ymyl_protected,
        }]
        
        # If node exists, delete it first then append (LanceDB delete by id)
        try:
            self._table.delete(f'id = "{node.id}"')
        except Exception:
            pass
        self._table.add(data)

    def update_active_status(self, node_id: str, is_active: bool) -> None:
        """Update node status in LanceDB."""
        try:
            self._table.update(where=f'id = "{node_id}"', values={"is_active": is_active})
        except Exception:
            pass

    def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """Search top_k nearest neighbors by cosine similarity."""
        query = self._table.search(query_vector).metric("cosine")
        if active_only:
            query = query.where("is_active = true")
        results = query.limit(top_k).to_list()
        return results

    def delete_node(self, node_id: str) -> None:
        """Delete vector record by id."""
        try:
            self._table.delete(f'id = "{node_id}"')
        except Exception:
            pass


vector_store = LanceVectorStore()
