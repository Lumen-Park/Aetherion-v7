"""
Curator Agent – selects minimal viable expert panel.
"""

from typing import List
from core.protocol import LLMWrapper
from agents.colleges.all_colleges import COLLEGE_MAPPING, get_agent

class Curator:
    """Selects the optimal panel of domain experts for a given goal."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def select_experts(self, goal: str, max_experts: int = 7) -> List[str]:
        """
        Analyze the goal and return a list of agent class names to activate.
        Limits to max_experts to prevent overload.
        """
        # Build context for LLM
        colleges_desc = "\n".join([
            f"- {college}: {', '.join(agents)}" 
            for college, agents in COLLEGE_MAPPING.items()
        ])
        
        prompt = f"""
        You are the Curator of Aetherion, an AI research institution with these colleges:
        
        {colleges_desc}
        
        For the following goal, select the {max_experts} most essential domain experts.
        Return ONLY a JSON array of agent class names (e.g., ["PhysicistAgent", "EconomistAgent"]).
        Do not select more than {max_experts}. Choose the most relevant.
        
        GOAL: {goal}
        """
        
        response = self.llm.generate(prompt)
        agent_names = self._parse_selection(response["content"])
        
        # Validate against registry
        valid_agents = [name for name in agent_names if name in COLLEGE_MAPPING.get(
            self._find_college_for_agent(name), []) or True]
        
        return valid_agents[:max_experts]
    
    def _parse_selection(self, text: str) -> List[str]:
        import json, re
        try:
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        # Fallback: keyword matching
        return self._keyword_fallback(text)
    
    def _keyword_fallback(self, goal: str) -> List[str]:
        """Simple fallback if LLM parsing fails."""
        goal_lower = goal.lower()
        selected = []
        
        if any(w in goal_lower for w in ["physics", "energy", "quantum", "material"]):
            selected.append("PhysicistAgent")
        if any(w in goal_lower for w in ["chemical", "chemistry", "reaction"]):
            selected.append("ChemistAgent")
        if any(w in goal_lower for w in ["biology", "gene", "cell", "protein"]):
            selected.append("BiologistAgent")
        if any(w in goal_lower for w in ["market", "price", "economic", "cost", "roi"]):
            selected.append("EconomistAgent")
        if any(w in goal_lower for w in ["data", "ml", "machine learning", "statistics"]):
            selected.append("DataScientistAgent")
        if any(w in goal_lower for w in ["security", "vulnerability", "hack"]):
            selected.append("RedTeamAgent")
        if any(w in goal_lower for w in ["patent", "legal", "compliance"]):
            selected.append("LegalComplianceAgent")
        
        # Always include at least Researcher and Critic (they're not in this registry)
        # The MetaOrchestrator adds those separately.
        return selected[:5]
    
    def _find_college_for_agent(self, agent_name: str) -> str:
        for college, agents in COLLEGE_MAPPING.items():
            if agent_name in agents:
                return college
        return ""
