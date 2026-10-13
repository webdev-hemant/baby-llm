"""Unit tests for Ebbinghaus Decay and YMYL retention."""

from datetime import datetime, timedelta, timezone
import pytest
from baby_llm.core.models import MemoryCategory, MemoryNode
from baby_llm.dream.decay import EbbinghausDecayEngine


def test_ymyl_retention_floor():
    engine = EbbinghausDecayEngine()
    # Health node from 100 days ago with YMYL protection
    health_node = MemoryNode(
        subject="user",
        predicate="allergic_to",
        object="penicillin",
        category=MemoryCategory.HEALTH,
        ymyl_protected=True,
        last_reinforced_at=datetime.now(timezone.utc) - timedelta(days=100),
    )
    r = engine.calculate_retention(health_node)
    assert r == 1.0


def test_ebbinghaus_decay_curve():
    engine = EbbinghausDecayEngine()
    # Trivia preference from 30 days ago without reinforcement
    trivia_node = MemoryNode(
        subject="user",
        predicate="ordered",
        object="latte",
        category=MemoryCategory.PREFERENCE,
        stability=1.0,
        ymyl_protected=False,
        last_reinforced_at=datetime.now(timezone.utc) - timedelta(days=30),
    )
    r = engine.calculate_retention(trivia_node)
    # exp(-30 / (1 * 1)) should be extremely small (< 0.001)
    assert r < 0.01


def test_stability_extension():
    engine = EbbinghausDecayEngine()
    # Node reinforced multiple times (stability = 8.0) after 10 days
    reinforced_node = MemoryNode(
        subject="user",
        predicate="works_on",
        object="Compiler",
        category=MemoryCategory.WORK,
        stability=8.0,
        ymyl_protected=False,
        last_reinforced_at=datetime.now(timezone.utc) - timedelta(days=10),
    )
    r = engine.calculate_retention(reinforced_node)
    # Importance for work is 2.0 -> exponent = -10 / (8 * 2) = -10/16 = -0.625 -> exp(-0.625) ~ 0.535
    assert r > 0.50


def test_offset_naive_datetime_handling():
    """Verify decay calculation handles offset-naive strings and datetimes without crashing."""
    engine = EbbinghausDecayEngine()
    # String from legacy SQLite DB without timezone offset
    naive_str_node = MemoryNode(
        subject="user",
        predicate="likes",
        object="coffee",
        category=MemoryCategory.PREFERENCE,
        last_reinforced_at="2026-09-30T06:53:28.464672",
    )
    r1 = engine.calculate_retention(naive_str_node, as_of=datetime.now(timezone.utc))
    assert 0.0 <= r1 <= 1.0

    # Naive datetime object as as_of
    naive_dt = datetime(2026, 10, 1, 12, 0, 0)
    r2 = engine.calculate_retention(naive_str_node, as_of=naive_dt)
    assert 0.0 <= r2 <= 1.0
