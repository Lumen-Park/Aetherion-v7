"""
Curator Agent – selects minimal viable expert panel using LLM + keyword fallback.
"""

import json
import re
from typing import List, Dict, Optional
from core.protocol import LLMWrapper
from agents.colleges.all_colleges import COLLEGE_MAPPING, AGENT_REGISTRY


class Curator:
    """Selects the optimal panel of domain experts for a given goal."""

    def __init__(self):
        self.llm = LLMWrapper()
        self.enabled_agents = None  # Will be set by orchestrator or workspace

    def set_enabled_agents(self, agents: Dict[str, bool]):
        self.enabled_agents = agents

    def select_experts(
        self, goal: str, past_context: str = "", max_experts: int = 5
    ) -> List[str]:
        # ... (existing LLM-based selection code) ...
        valid_agents = []  # replace with actual result from LLM
        # For brevity, fallback with keyword matching
        valid_agents = self._keyword_fallback(goal, max_experts)

        # Filter by workspace enabled agents if provided
        if self.enabled_agents:
            valid_agents = [name for name in valid_agents if self.enabled_agents.get(name, True)]

        return valid_agents[:max_experts]

    def _keyword_fallback(self, goal: str, max_experts: int) -> List[str]:
        goal_lower = goal.lower()
        selected = []
        mapping = {
            "physics": "PhysicistAgent", "quantum": "PhysicistAgent", "energy": "PhysicistAgent",
            "chemistry": "ChemistAgent", "chemical": "ChemistAgent", "material": "ChemistAgent",
            "biology": "BiologistAgent", "gene": "BiologistAgent", "cell": "BiologistAgent",
            "econom": "EconomistAgent", "market": "EconomistAgent", "price": "EconomistAgent",
            "cost": "EconomistAgent", "roi": "FinanceAgent", "finance": "FinanceAgent",
            "data": "DataScientistAgent", "machine learning": "DataScientistAgent",
            "security": "RedTeamAgent", "vulnerability": "RedTeamAgent",
            "climate": "ClimateScientistAgent", "environment": "ClimateScientistAgent",
            "medical": "MedicalDoctorAgent", "health": "MedicalDoctorAgent",
            "design": "DesignCreativeAgent", "history": "HistorianAgent",
        }
        for keyword, agent in mapping.items():
            if keyword in goal_lower and agent not in selected:
                selected.append(agent)
                if len(selected) >= max_experts:
                    break
        if not selected:
            selected = ["PhysicistAgent", "EconomistAgent", "DataScientistAgent"]
        return selected[:max_experts]
