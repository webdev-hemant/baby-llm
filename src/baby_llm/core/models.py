"""Core data models for Baby LLM."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


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


class MemoryNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    predicate: str
    object: str
    category: MemoryCategory = MemoryCategory.PREFERENCE
    confidence: float = 1.0
    stability: float = 1.0
    last_reinforced_at: datetime = Field(default_factory=utc_now)
    valid_from: datetime = Field(default_factory=utc_now)
    invalid_from: Optional[datetime] = None  # None indicates active fact
    ymyl_protected: bool = False
    source_turn_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)

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
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    associated_node_id: Optional[str] = None


class RetrievedMemory(BaseModel):
    node: MemoryNode
    score: float
    retrieval_source: str  # "bm25", "vector", or "hybrid"
