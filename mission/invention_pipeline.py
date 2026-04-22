"""
Invention Pipeline – Idea → Theory → Hypothesis → Simulation → Design → Blueprint → LaTeX.
"""

import os
import json
import time
from typing import Dict, List
from core.protocol import LLMWrapper
from agents.council.council import AetherionCouncil
from agents.colleges.all_colleges import get_agent
from agents.governance.curator import Curator

class InventionPipeline:
    def __init__(self):
        self.llm = LLMWrapper()
        self.council = AetherionCouncil()
        self.state = {}
    
    def run(self, idea: str) -> str:
        """Execute full invention pipeline, return LaTeX document path."""
        self.state['idea'] = idea
        
        # Phase 1: Ideation
        self.state['refined_idea'] = self._refine_idea(idea)
        
        # Phase 2: Theory & Hypothesis
        self.state['theory'] = self._develop_theory()
        self.state['hypothesis'] = self._formulate_hypothesis()
        
        # Phase 3: Simulation (mental)
        self.state['simulation'] = self._simulate()
        
        # Phase 4: Design
        self.state['design'] = self._design()
        
        # Phase 5: College Review
        self.state['expert_reviews'] = self._college_review()
        
        # Phase 6: Council Review
        self.state['council_verdict'] = self.council.deliberate(
            json.dumps(self.state), self.state['refined_idea']
        )
        
        # Phase 7: Blueprint & LaTeX
        latex_path = self._generate_latex()
        return latex_path
    
    def _refine_idea(self, idea: str) -> str:
        prompt = f"Refine this invention idea into a precise, actionable concept: {idea}"
        return self.llm.generate(prompt)["content"]
    
    def _develop_theory(self) -> str:
        prompt = f"Develop a scientific theory explaining how this could work: {self.state['refined_idea']}"
        return self.llm.generate(prompt, system="You are a theoretical scientist.")["content"]
    
    def _formulate_hypothesis(self) -> str:
        prompt = f"Formulate a testable hypothesis based on this theory: {self.state['theory']}"
        return self.llm.generate(prompt)["content"]
    
    def _simulate(self) -> str:
        prompt = f"Mentally simulate this invention and identify potential failure points: {self.state['refined_idea']}"
        return self.llm.generate(prompt)["content"]
    
    def _design(self) -> Dict:
        prompt = f"Create a detailed design specification for: {self.state['refined_idea']}"
        response = self.llm.generate(prompt)
        return {"spec": response["content"]}
    
    def _college_review(self) -> Dict:
        curator = Curator()
        experts = curator.select_experts(self.state['refined_idea'], max_experts=5)
        reviews = {}
        for name in experts:
            agent = get_agent(name)
            if agent:
                analysis = agent.analyze(self.state['refined_idea'])
                reviews[name] = analysis
        return reviews
    
    def _generate_latex(self) -> str:
        prompt = f"""
        Generate a professional LaTeX document for this invention:
        
        Idea: {self.state['idea']}
        Theory: {self.state['theory']}
        Hypothesis: {self.state['hypothesis']}
        Design: {self.state['design']}
        Expert Reviews: {self.state['expert_reviews']}
        
        Include sections: Abstract, Introduction, Theory, Design, Feasibility Analysis, Conclusion.
        Use proper LaTeX formatting with figures placeholder.
        """
        latex_content = self.llm.generate(prompt)["content"]
        os.makedirs("./latex_docs", exist_ok=True)
        filename = f"invention_{int(time.time())}.tex"
        path = os.path.join("./latex_docs", filename)
        with open(path, 'w') as f:
            f.write(latex_content)
        return path
