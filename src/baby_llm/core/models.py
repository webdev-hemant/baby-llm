"""Core data models for Baby LLM."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator
import uuid


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_utc(dt: Union[datetime, str, None]) -> Optional[datetime]:
    """Ensures any datetime or ISO string is converted into a UTC-aware datetime."""
    if dt is None:
        return None
    if isinstance(dt, str):
        cleaned = dt.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class MemoryCategory(str, Enum):
    LIFESTYLE = "lifestyle"
    HEALTH = "health"
    FINANCE = "finance"
    WORK = "work"
    RELATIONSHIP = "relationship"
    GOAL = "goal"
    PREFERENCE = "preference"


class CommitmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"


class InteractionTurn(BaseModel):
    turn_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = "default"
    timestamp: datetime = Field(default_factory=utc_now)
    user_input: str
    assistant_response: str
    sentiment_tag: Optional[str] = None
    processed_in_dream: bool = False

    @field_validator("timestamp", mode="before")
    @classmethod
    def _coerce_utc_timestamp(cls, v):
        return ensure_utc(v)


class MemoryNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    predicate: str
    object: str
    category: MemoryCategory = MemoryCategory.PREFERENCE
    scope: str = "global"
    confidence: float = 1.0
    stability: float = 1.0
    last_reinforced_at: datetime = Field(default_factory=utc_now)
    valid_from: datetime = Field(default_factory=utc_now)
    invalid_from: Optional[datetime] = None  # None indicates active fact
    ymyl_protected: bool = False
    source_turn_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("last_reinforced_at", "valid_from", "invalid_from", "created_at", mode="before")
    @classmethod
    def _coerce_utc_node(cls, v):
        return ensure_utc(v)

    @property
    def is_active(self) -> bool:
        return self.invalid_from is None

    def to_readable_fact(self) -> str:
        return f"{self.subject} {self.predicate} {self.object}"


class Commitment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    status: CommitmentStatus = CommitmentStatus.PENDING
    target_deadline: Optional[datetime] = None
    detected_at: datetime = Field(default_factory=utc_now)
    resolved_at: Optional[datetime] = None
    associated_node_id: Optional[str] = None

    @field_validator("target_deadline", "detected_at", "resolved_at", mode="before")
    @classmethod
    def _coerce_utc_commitment(cls, v):
        return ensure_utc(v)


class RetrievedMemory(BaseModel):
    node: MemoryNode
    score: float
    retrieval_source: str  # "bm25", "vector", or "hybrid"
