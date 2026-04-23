"""
Curator Agent – selects minimal viable expert panel using LLM + keyword fallback.
Now filters by workspace‑enabled agents.
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
        self.enabled_agents: Optional[Dict[str, bool]] = None

    def set_enabled_agents(self, agents: Dict[str, bool]):
        """
        Set the workspace‑specific enabled/disabled state for agents.
        Only enabled agents will be returned by select_experts.
        """
        self.enabled_agents = agents

    def select_experts(
        self, goal: str, past_context: str = "", max_experts: int = 5
    ) -> List[str]:
        """
        Select the best domain experts for a given goal.
        Considers the workspace's enabled/disabled agent list if provided.
        """
        colleges_desc = self._build_colleges_description()
        prompt = f"""
        You are the Curator of Aetherion, an AI research institution with these colleges:

        {colleges_desc}

        Past relevant context: {past_context if past_context else 'None'}

        For the following goal, select the {max_experts} most essential domain experts.
        Consider interdisciplinary needs. Choose only from the agent names listed above.

        GOAL: {goal}

        Return ONLY a JSON array of agent class names,
        e.g., ["PhysicistAgent", "EconomistAgent"].
        Do not select more than {max_experts}.
        Do not include agents not in the list.
        """

        try:
            response = self.llm.generate(prompt)
            agent_names = self._parse_selection(response["content"])
        except Exception:
            agent_names = []

        # Validate against the registry of existing agents
        valid_agents = [name for name in agent_names if name in AGENT_REGISTRY]

        # If LLM selection failed or produced no valid agents, use keyword fallback
        if not valid_agents:
            valid_agents = self._keyword_fallback(goal, max_experts)

        # Filter by workspace enabled agents if provided
        if self.enabled_agents is not None:
            valid_agents = [
                name for name in valid_agents
                if self.enabled_agents.get(name, True)
            ]

        return valid_agents[:max_experts]

    def _build_colleges_description(self) -> str:
        """Build a textual description of all available colleges and their agents."""
        lines = []
        for college, agents in COLLEGE_MAPPING.items():
            lines.append(f"- {college}: {', '.join(agents)}")
        return "\n".join(lines)

    def _parse_selection(self, text: str) -> List[str]:
        """Extract a JSON array of agent names from the LLM response."""
        try:
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return []

    def _keyword_fallback(self, goal: str, max_experts: int) -> List[str]:
        """
        Fallback method that selects agents based on keyword matching
        when the LLM call fails or returns unusable output.
        """
        goal_lower = goal.lower()
        selected = []

        # Comprehensive keyword mapping
        mapping = {
            "physics": "PhysicistAgent",
            "quantum": "PhysicistAgent",
            "energy": "PhysicistAgent",
            "battery": "PhysicistAgent",
            "chemistry": "ChemistAgent",
            "chemical": "ChemistAgent",
            "material": "ChemistAgent",
            "biology": "BiologistAgent",
            "gene": "BiologistAgent",
            "cell": "BiologistAgent",
            "math": "MathematicianAgent",
            "statistic": "StatisticianAgent",
            "econom": "EconomistAgent",
            "market": "EconomistAgent",
            "price": "EconomistAgent",
            "cost": "EconomistAgent",
            "roi": "FinanceAgent",
            "finance": "FinanceAgent",
            "business": "EnterpriseArchitectAgent",
            "enterprise": "EnterpriseArchitectAgent",
            "data": "DataScientistAgent",
            "machine learning": "DataScientistAgent",
            "ml": "DataScientistAgent",
            "security": "RedTeamAgent",
            "vulnerability": "RedTeamAgent",
            "hack": "RedTeamAgent",
            "crypto": "CryptographerAgent",
            "encrypt": "CryptographerAgent",
            "patent": "PatentExaminerAgent",
            "legal": "LegalComplianceAgent",
            "compliance": "LegalComplianceAgent",
            "regulatory": "RegulatoryAffairsAgent",
            "climate": "ClimateScientistAgent",
            "environment": "ClimateScientistAgent",
            "ecology": "EcologistAgent",
            "medical": "MedicalDoctorAgent",
            "health": "MedicalDoctorAgent",
            "drug": "PharmacologistAgent",
            "pharma": "PharmacologistAgent",
            "design": "DesignCreativeAgent",
            "ux": "DesignCreativeAgent",
            "ui": "DesignCreativeAgent",
            "history": "HistorianAgent",
            "ethics": "PhilosopherEthicistAgent",
            "philosophy": "PhilosopherEthicistAgent",
            "future": "FuturistAgent",
            "system": "SystemsThinkerAgent",
        }

        for keyword, agent in mapping.items():
            if keyword in goal_lower and agent not in selected:
                selected.append(agent)
                if len(selected) >= max_experts:
                    break

        # Default fallback if nothing matches
        if not selected:
            selected = ["PhysicistAgent", "EconomistAgent", "DataScientistAgent"]

        return selected[:max_experts]

    def get_agent_descriptions(self, agent_names: List[str]) -> Dict[str, str]:
        """
        Return a short description for each agent name,
        useful for debugging or UI display.
        """
        descriptions = {}
        for name in agent_names:
            cls = AGENT_REGISTRY.get(name)
            if cls:
                descriptions[name] = f"{cls.college} - {cls.expertise}"
        return descriptions
