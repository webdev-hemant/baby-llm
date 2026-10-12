"""Architectural Invariant and Policy Guardrail Engine for External AI Agents."""

import re
from typing import Any, Dict, List, Optional
from baby_llm.core.models import MemoryCategory
from baby_llm.retrieval.hybrid import hybrid_retriever
from baby_llm.runtime.llm_provider import llm_provider


CONTRASTIVE_MARKERS = [
    r"\bavoids?\b",
    r"\bforbids?\b",
    r"\bprohibits?\b",
    r"\bdeprecated?\b",
    r"\bnever\b",
    r"\bmust not\b",
    r"\bdo not\b",
    r"\bdisallows?\b",
    r"\bno\b",
    r"\bprefers?\b",
    r"\benforces?\b",
    r"\brequires?\b",
    r"\balways\b",
    r"\bstrictly\b",
]


class InvariantGuardrail:
    """Verifies intended code and architecture changes against stored memory invariants."""

    def __init__(self, retriever=hybrid_retriever, provider=llm_provider):
        self.retriever = retriever
        self.provider = provider

    def check_proposal(self, proposal: str, scope: str = "global") -> str:
        """
        Audits a technical proposal against active memory nodes in the given scope.
        Returns a formatted pass/warning string.
        """
        clean_prop = proposal.strip()
        if not clean_prop:
            return "Empty proposal provided. Nothing to verify."

        # 1. Retrieve relevant memories
        memories = self.retriever.retrieve(query=clean_prop, top_k=6, scope=scope)
        if not memories:
            return (
                f"✅ PASSED: No conflicting invariants or architectural constraints found in scope '{scope}'.\n"
                "Safe to proceed."
            )

        active_context = []
        violations = []

        # 2. Heuristic scan of retrieved memories for explicit conflicts
        prop_words = set(re.findall(r"\b[a-zA-Z0-9_\-\.]{3,}\b", clean_prop.lower()))

        for m in memories:
            node = m.node
            fact_str = f"[{node.category.value.upper()}] {node.to_readable_fact()}"
            active_context.append(f"- {fact_str} (ID: {node.id[:8]}, Scope: {node.scope})")

            # Check if this node contains a negative constraint
            fact_lower = fact_str.lower()
            has_contrast = any(re.search(marker, fact_lower) for marker in CONTRASTIVE_MARKERS)

            if has_contrast:
                # Check for overlap between proposal keywords and constraint keywords
                node_words = set(re.findall(r"\b[a-zA-Z0-9_\-\.]{3,}\b", fact_lower))
                # Exclude common stopwords
                common_stops = {"user", "noted", "true", "false", "this", "that", "with", "from", "have", "will"}
                overlap = (prop_words & node_words) - common_stops

                if overlap:
                    # Check if the node specifically expresses avoidance/forbiddance of the overlapped term
                    for term in overlap:
                        neg_patterns = [
                            rf"avoid[s]?\s+.*{re.escape(term)}",
                            rf"forbid[s]?\s+.*{re.escape(term)}",
                            rf"prohibit[s]?\s+.*{re.escape(term)}",
                            rf"no\s+{re.escape(term)}",
                            rf"never\s+.*{re.escape(term)}",
                            rf"not\s+.*{re.escape(term)}",
                        ]
                        if any(re.search(p, fact_lower) for p in neg_patterns):
                            violations.append({
                                "node": node,
                                "term": term,
                                "fact": fact_str,
                            })

        # 3. Formulate response
        if violations:
            report_lines = [
                "⚠️ INVARIANT VIOLATION DETECTED:",
            ]
            for v in violations:
                report_lines.append(f"• Conflicting Memory: {v['fact']} (ID: {v['node'].id[:8]})")
                report_lines.append(f"  Conflict Term: '{v['term']}' is restricted or forbidden by active policy.")
            report_lines.append("\nActive Constraints Considered:")
            report_lines.extend(active_context[:4])
            report_lines.append("\nRecommendation: Refactor your plan to respect the established policy above.")
            return "\n".join(report_lines)

        # Passed cleanly
        pass_lines = [
            f"✅ PASSED: No conflicting invariants detected for proposal in scope '{scope}'.",
            "\nActive Context Considered:",
        ]
        pass_lines.extend(active_context[:4])
        return "\n".join(pass_lines)

    def _llm_verify(self, proposal: str, context_facts: List[str]) -> Optional[str]:
        """Optional LLM semantic contradiction verification."""
        try:
            facts_text = "\n".join(f"- {f}" for f in context_facts)
            prompt = (
                "You are an architectural invariant guardrail.\n"
                f"Proposed Technical Action: {proposal}\n\n"
                f"Active Rules and Memories:\n{facts_text}\n\n"
                "Does the proposed action violate, contradict, or break any of the active rules or preferences?\n"
                "If YES, reply with 'VIOLATION: <exact reason>'.\n"
                "If NO, reply with 'OK'."
            )
            raw = self.provider.chat_sync([{"role": "user", "content": prompt}])
            if isinstance(raw, str):
                resp = raw.strip()
                if resp.startswith("VIOLATION:"):
                    return f"⚠️ INVARIANT VIOLATION DETECTED:\n• {resp.removeprefix('VIOLATION:').strip()}\n\nRecommendation: Align implementation with active rules."
        except Exception:
            pass
        return None


guardrail = InvariantGuardrail()
