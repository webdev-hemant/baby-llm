"""Atomic fact extraction pipeline using local SLMs (SmolLM2 / Qwen2.5)."""

import json
import re
from typing import Any, Dict, List, Optional
from baby_llm.config import settings
from baby_llm.core.models import InteractionTurn, MemoryCategory
from baby_llm.runtime.llm_provider import llm_provider


EXTRACTION_PROMPT = """You are an expert cognitive memory extraction system.
Analyze the following conversation turn between a User and Assistant.
Extract any durable personal facts, preferences, relationships, goals, commitments, or health/financial details stated by the user.

Output a strict JSON array of objects with the following schema:
[
  {
    "subject": "user",
    "predicate": "short verb or attribute phrase (e.g. works_at, lives_in, prefers, allergic_to, goal_is)",
    "object": "concise factual value",
    "category": "lifestyle | health | finance | work | relationship | goal | preference",
    "confidence": 0.95,
    "ymyl": false
  }
]

Do not extract temporary banter or pleasantries. If no personal facts were shared, return [].
JSON ONLY:
"""


AGENT_REMEMBER_PROMPT = """You are a technical knowledge extraction engine.
Analyze the following statement, architectural rule, or constraint:
"{text}"

Extract the atomic facts, technical constraints, or architectural rules.
Output a strict JSON array of objects with the schema:
[
  {
    "subject": "entity or user (e.g. team, project, user)",
    "predicate": "relationship or rule (e.g. enforces, forbids, uses, prefers, avoids)",
    "object": "target value or technology",
    "category": "work | preference | goal",
    "confidence": 0.95,
    "ymyl": false
  }
]
Do not invent facts not in the statement.
JSON ONLY:
"""


class FactExtractor:
    def __init__(self, provider=llm_provider):
        self.provider = provider

    def extract_from_turn(self, turn: InteractionTurn) -> List[Dict[str, Any]]:
        """Extract atomic facts from an interaction turn."""
        content = f"User: {turn.user_input}\nAssistant: {turn.assistant_response}"
        messages = [
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": content},
        ]

        try:
            raw_response = self.provider.chat_sync(messages)
            return self._parse_json_response(raw_response)
        except Exception:
            # Fallback heuristic parser if local LLM is offline or returns malformed text
            return self._heuristic_fallback(turn.user_input)

    def extract_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract atomic facts from free-form natural language text."""
        clean = text.strip()
        messages = [
            {"role": "user", "content": AGENT_REMEMBER_PROMPT.replace("{text}", clean)},
        ]

        try:
            raw_response = self.provider.chat_sync(messages)
            results = self._parse_json_response(raw_response)
            if results:
                return results
        except Exception:
            pass

        # Try heuristic fallback
        heuristics = self._heuristic_fallback(clean)
        if heuristics:
            return heuristics

        # Default fallback: structured single fact
        return [{
            "subject": "user",
            "predicate": "noted",
            "object": clean,
            "category": MemoryCategory.PREFERENCE,
            "confidence": 0.9,
            "ymyl": False,
        }]

    def _parse_json_response(self, text: str) -> List[Dict[str, Any]]:
        clean_text = text.strip()
        # Find JSON array using regex
        match = re.search(r"\[\s*\{.*\}\s*\]", clean_text, re.DOTALL)
        if match:
            clean_text = match.group(0)
        elif clean_text.startswith("```json"):
            clean_text = clean_text.removeprefix("```json").removesuffix("```").strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text.removeprefix("```").removesuffix("```").strip()

        try:
            data = json.loads(clean_text)
            if isinstance(data, list):
                valid_items = []
                for item in data:
                    if "subject" in item and "predicate" in item and "object" in item:
                        category_str = item.get("category", "preference").lower()
                        if category_str not in [c.value for c in MemoryCategory]:
                            category_str = "preference"
                        valid_items.append({
                            "subject": str(item["subject"]).strip(),
                            "predicate": str(item["predicate"]).strip(),
                            "object": str(item["object"]).strip(),
                            "category": MemoryCategory(category_str),
                            "confidence": float(item.get("confidence", 0.9)),
                            "ymyl": bool(item.get("ymyl", category_str in ("health", "finance"))),
                        })
                return valid_items
        except json.JSONDecodeError:
            pass
        return []

    def _heuristic_fallback(self, user_text: str) -> List[Dict[str, Any]]:
        """Basic regex rules for key user assertions when SLM is offline."""
        facts = []
        text = user_text.strip()

        # "I live in X"
        live_match = re.search(r"\bi live in ([a-zA-Z\s,]+)", text, re.IGNORECASE)
        if live_match:
            facts.append({
                "subject": "user",
                "predicate": "lives_in",
                "object": live_match.group(1).strip().rstrip("."),
                "category": MemoryCategory.LIFESTYLE,
                "confidence": 0.95,
                "ymyl": False,
            })

        # "I work as X" or "I am a X"
        work_match = re.search(r"\bi work as (?:a|an)?\s*([a-zA-Z\s]+)", text, re.IGNORECASE)
        if work_match:
            facts.append({
                "subject": "user",
                "predicate": "works_as",
                "object": work_match.group(1).strip().rstrip("."),
                "category": MemoryCategory.WORK,
                "confidence": 0.95,
                "ymyl": False,
            })

        # "I am allergic to X"
        allergy_match = re.search(r"\bi am allergic to ([a-zA-Z\s,]+)", text, re.IGNORECASE)
        if allergy_match:
            facts.append({
                "subject": "user",
                "predicate": "allergic_to",
                "object": allergy_match.group(1).strip().rstrip("."),
                "category": MemoryCategory.HEALTH,
                "confidence": 1.0,
                "ymyl": True,
            })

        return facts


fact_extractor = FactExtractor()
