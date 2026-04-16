"""
Base class for all college domain experts.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.protocol import LLMWrapper, AgentMessage, Priority

class CollegeAgent(ABC):
    """Abstract base for all 67+ domain agents."""
    
    college: str = "Unknown"
    expertise: str = "General"
    
    def __init__(self, name: str, model: str = "llama3"):
        self.name = name
        self.llm = LLMWrapper(model=model)
        self.system_prompt = self._build_system_prompt()
    
    @abstractmethod
    def _build_system_prompt(self) -> str:
        """Each agent defines its own expert system prompt."""
        pass
    
    def analyze(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze a query from the perspective of this domain expert.
        Returns a structured assessment.
        """
        prompt = f"""
        As a {self.expertise} expert, analyze the following:
        
        QUERY: {query}
        
        CONTEXT: {context if context else 'None provided'}
        
        Provide your analysis in JSON format with these fields:
        - assessment: your expert evaluation
        - confidence: 0.0 to 1.0
        - concerns: list of potential issues or risks
        - recommendations: actionable advice
        - references: key concepts or sources to consult
        """
        
        response = self.llm.generate(prompt, system=self.system_prompt)
        return self._parse_response(response)
    
    def testify(self, findings: Dict, council_question: str) -> Dict[str, Any]:
        """Provide expert testimony to the Council on a specific question."""
        prompt = f"""
        You are providing expert testimony to the Aetherion Council.
        
        FINDINGS: {findings}
        COUNCIL QUESTION: {council_question}
        
        Provide a concise, evidence-based answer in JSON:
        - answer: your expert opinion
        - confidence: 0.0 to 1.0
        - dissenting_view: any alternative perspective
        """
        response = self.llm.generate(prompt, system=self.system_prompt)
        return self._parse_response(response)
    
    def _parse_response(self, response: Dict) -> Dict:
        """Extract JSON from LLM response."""
        import json, re
        content = response.get("content", "")
        try:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return {
            "assessment": content[:500],
            "confidence": response.get("confidence", 0.5),
            "concerns": [],
            "recommendations": [],
            "references": []
        }
    
    def __repr__(self):
        return f"<{self.name} ({self.college})>"
