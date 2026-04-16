"""
Researcher, Developer, Tester, and other pipeline agents.
"""

from core.protocol import LLMWrapper

class Researcher:
    def __init__(self):
        self.llm = LLMWrapper()
    
    def execute(self, query: str) -> Dict:
        prompt = f"Research thoroughly: {query}. Include citations and key findings."
        return self.llm.generate(prompt, system="You are a senior researcher.")

class Developer:
    def __init__(self):
        self.llm = LLMWrapper()
    
    def write_code(self, research: str, goal: str) -> Dict:
        prompt = f"""
        Based on this research, write clean, production‑ready Python code to achieve: {goal}
        
        Research: {research}
        
        Return only the code block.
        """
        return self.llm.generate(prompt, system="You are an expert Python developer.")

class Tester:
    def __init__(self):
        self.llm = LLMWrapper()
    
    def test(self, code: str) -> Dict:
        # In production, this would run in Docker sandbox
        prompt = f"Analyze this code for bugs and edge cases: {code}"
        response = self.llm.generate(prompt)
        # Simplified pass/fail
        passed = "error" not in response["content"].lower()
        return {"passed": passed, "details": response["content"]}
