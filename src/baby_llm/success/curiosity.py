"""Gentle Curiosity Protocol for unobtrusive personal learning."""

from typing import Optional, Set
import re


class GentleCuriosityEngine:
    def __init__(self, max_probes_per_session: int = 1):
        self.max_probes_per_session = max_probes_per_session
        self._probes_asked_this_session = 0
        self._asked_entities: Set[str] = set()

    def reset_session(self) -> None:
        self._probes_asked_this_session = 0

    def can_probe(self) -> bool:
        return self._probes_asked_this_session < self.max_probes_per_session

    def evaluate_turn_for_probe(self, user_input: str) -> Optional[str]:
        """
        Detects ambiguous entities (e.g., 'Project Alpha', 'Dr. Smith')
        and formats at most ONE gentle clarifying question.
        """
        if not self.can_probe():
            return None

        # Look for named projects or ambiguous terms: "project [A-Za-z0-9]+"
        match = re.search(r"\bproject\s+([a-zA-Z0-9_\-]+)\b", user_input, re.IGNORECASE)
        if match:
            project_name = match.group(1).title()
            if project_name not in self._asked_entities:
                self._probes_asked_this_session += 1
                self._asked_entities.add(project_name)
                return f"By the way, you mentioned Project {project_name}—is this an internal initiative or a client milestone?"

        return None


curiosity_engine = GentleCuriosityEngine()
