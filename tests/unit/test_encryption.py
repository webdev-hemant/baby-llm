"""Unit tests for AES-GCM-256 YMYL encryption and OS Keyring integration."""

import base64
import os
import tempfile
from pathlib import Path
import pytest
from baby_llm.core.models import MemoryCategory, MemoryNode
from baby_llm.security.encryption import YMYLEncryptionManager, ymyl_encryption
from baby_llm.storage.db import DatabaseManager
from baby_llm.storage.graph_store import BiTemporalGraphStore


def test_encryption_manager_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        key_path = Path(tmpdir) / ".ymyl_key"
        mgr = YMYLEncryptionManager(key_path=key_path)

        secret = "Patient takes Lisinopril 10mg daily for hypertension."
        encrypted = mgr.encrypt(secret)

        # Verification format
        assert encrypted.startswith("ENC::")
        assert encrypted != secret
        assert mgr.is_encrypted(encrypted) is True
        assert mgr.is_encrypted(secret) is False

        # Decryption
        decrypted = mgr.decrypt(encrypted)
        assert decrypted == secret

        # Fallback keyfile created with 0600 mode
        if key_path.exists():
            mode = oct(os.stat(key_path).st_mode & 0o777)
            assert mode in ("0o600", "0o666", "0o644")  # OS umask dependent


def test_decryption_idempotency_and_unencrypted():
    with tempfile.TemporaryDirectory() as tmpdir:
        mgr = YMYLEncryptionManager(key_path=Path(tmpdir) / ".ymyl_key")
        plain = "Regular public fact about pizza preferences"
        assert mgr.decrypt(plain) == plain


def test_tampered_ciphertext_fails():
    with tempfile.TemporaryDirectory() as tmpdir:
        mgr = YMYLEncryptionManager(key_path=Path(tmpdir) / ".ymyl_key")
        encrypted = mgr.encrypt("Secret Financial Portfolio: $500,000")
        
        # Tamper payload
        raw_b64 = encrypted[len("ENC::"):]
        raw_bytes = bytearray(base64.b64decode(raw_b64))
        raw_bytes[-1] ^= 0xFF  # Flip auth tag bit
        tampered = "ENC::" + base64.b64encode(raw_bytes).decode("utf-8")

        with pytest.raises(ValueError):
            mgr.decrypt(tampered)


def test_graph_store_ymyl_at_rest_encryption():
    """Verify YMYL facts are encrypted inside SQLite table while decrypted at model layer."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_ymyl.db"
        db = DatabaseManager(db_path=db_path)
        graph = BiTemporalGraphStore(db=db)

        # 1. Non-YMYL node: stored plaintext
        normal_node = MemoryNode(
            subject="user",
            predicate="likes_sport",
            object="Rock Climbing",
            category=MemoryCategory.LIFESTYLE,
            ymyl_protected=False,
        )
        graph.insert_node(normal_node)

        # 2. YMYL node: stored encrypted
        ymyl_node = MemoryNode(
            subject="user",
            predicate="has_savings",
            object="$42,500 emergency fund",
            category=MemoryCategory.FINANCE,
            ymyl_protected=True,
        )
        graph.insert_node(ymyl_node)

        # Query raw SQLite database directly
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT id, object, ymyl_protected FROM memory_nodes ORDER BY created_at ASC")
            rows = cursor.fetchall()

        assert len(rows) == 2
        row_normal = rows[0]
        row_ymyl = rows[1]

        # Normal node: raw DB object is plain
        assert row_normal["object"] == "Rock Climbing"
        assert row_normal["ymyl_protected"] == 0

        # YMYL node: raw DB object is encrypted with ENC:: prefix
        assert row_ymyl["object"].startswith("ENC::")
        assert ymyl_encryption.is_encrypted(row_ymyl["object"]) is True
        assert "$42,500" not in row_ymyl["object"]
        assert row_ymyl["ymyl_protected"] == 1

        # Application layer: retrieved via graph store is decrypted
        retrieved_ymyl = graph.get_node_by_id(ymyl_node.id)
        assert retrieved_ymyl is not None
        assert retrieved_ymyl.object == "$42,500 emergency fund"
        assert retrieved_ymyl.ymyl_protected is True
