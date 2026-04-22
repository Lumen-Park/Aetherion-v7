"""
Invention Pipeline – Idea → Theory → Hypothesis → Simulation → Design → Blueprint → LaTeX.
"""

import os
import json
import time
from typing import Dict
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
        self.state['idea'] = idea
        self.state['refined_idea'] = self._refine_idea(idea)
        self.state['theory'] = self._develop_theory()
        self.state['hypothesis'] = self._formulate_hypothesis()
        self.state['simulation'] = self._simulate()
        self.state['design'] = self._design()
        self.state['expert_reviews'] = self._college_review()
        self.state['council_verdict'] = self.council.deliberate(json.dumps(self.state), self.state['refined_idea'])
        return self._generate_latex()

    def _refine_idea(self, idea: str) -> str:
        return self.llm.generate(f"Refine this invention idea: {idea}")["content"]

    def _develop_theory(self) -> str:
        return self.llm.generate(f"Develop a scientific theory: {self.state['refined_idea']}", system="You are a theoretical scientist.")["content"]

    def _formulate_hypothesis(self) -> str:
        return self.llm.generate(f"Formulate a testable hypothesis: {self.state['theory']}")["content"]

    def _simulate(self) -> str:
        return self.llm.generate(f"Mentally simulate this invention and identify failure points: {self.state['refined_idea']}")["content"]

    def _design(self) -> Dict:
        return {"spec": self.llm.generate(f"Create design specification: {self.state['refined_idea']}")["content"]}

    def _college_review(self) -> Dict:
        curator = Curator()
        experts = curator.select_experts(self.state['refined_idea'], max_experts=5)
        reviews = {}
        for name in experts:
            agent = get_agent(name)
            if agent:
                reviews[name] = agent.analyze(self.state['refined_idea'])
        return reviews

    def _generate_latex(self) -> str:
        prompt = f"Generate a professional LaTeX document for this invention:\nIdea: {self.state['idea']}\nTheory: {self.state['theory']}\nHypothesis: {self.state['hypothesis']}\nDesign: {self.state['design']}\nExpert Reviews: {self.state['expert_reviews']}"
        latex = self.llm.generate(prompt)["content"]
        os.makedirs("./latex_docs", exist_ok=True)
        path = os.path.join("./latex_docs", f"invention_{int(time.time())}.tex")
        with open(path, 'w') as f:
            f.write(latex)
        return path
