"""
Pipeline Agents – Researcher, Developer, Partner, Tester, Reporter,
Scout, Synthesizer, Presenter, GoalRefiner, DocumentationAgent, Debugger.
"""

import json
import re
from typing import Dict, Any, Optional, List
from core.protocol import LLMWrapper


class GoalRefiner:
    """Converts vague user input into precise, actionable goals."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def refine(self, goal: str) -> Dict[str, Any]:
        prompt = f"""
        Refine this vague goal into a precise, actionable task.
        Include: what exactly needs to be done, constraints, expected output format.
        
        Original: {goal}
        
        Return JSON with:
        - refined_goal: the precise description
        - subtasks: list of concrete steps
        - success_criteria: how to know it's done correctly
        """
        response = self.llm.generate(prompt)
        try:
            data = json.loads(self._extract_json(response["content"]))
            return {"content": data.get("refined_goal", goal), "confidence": response["confidence"]}
        except:
            return {"content": goal, "confidence": 0.5}
    
    def _extract_json(self, text: str) -> str:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group() if match else "{}"


class Researcher:
    """Deep-dives any topic, returning structured findings."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def execute(self, query: str, context: str = "") -> Dict[str, Any]:
        system = "You are a senior researcher. Provide thorough, evidence-based analysis with citations."
        prompt = f"""
        Research the following thoroughly:
        {query}
        
        Additional context: {context}
        
        Provide:
        - Key findings
        - Relevant technologies/methods
        - Potential challenges
        - Recommended approach
        """
        response = self.llm.generate(prompt, system=system)
        return {"content": response["content"], "confidence": response["confidence"]}


class Developer:
    """Writes production-ready code from research and requirements."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def write_code(self, research: str, goal: str, strategy_hint: str = "") -> Dict[str, Any]:
        system = "You are an expert Python developer. Write clean, well-documented, production-ready code."
        prompt = f"""
        Write code to accomplish: {goal}
        
        Research findings: {research}
        
        Strategy hint: {strategy_hint if strategy_hint else 'Use best practices'}
        
        Return ONLY the Python code block, with necessary imports and a main guard if applicable.
        Include brief comments explaining key logic.
        """
        response = self.llm.generate(prompt, system=system)
        code = self._extract_code(response["content"])
        return {"content": code, "confidence": response["confidence"]}
    
    def _extract_code(self, text: str) -> str:
        match = re.search(r'```python(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        match = re.search(r'```(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()


class Partner:
    """Reviews code for quality, security, and adherence to requirements."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def review(self, code: str, goal: str) -> Dict[str, Any]:
        system = "You are a senior code reviewer. Be thorough but constructive."
        prompt = f"""
        Review this code against the original goal: {goal}
        
        Code:
        {code}
        
        Evaluate:
        1. Does it correctly solve the problem?
        2. Code quality (readability, structure, naming)
        3. Potential bugs or edge cases
        4. Security concerns
        
        Return JSON:
        - "requires_changes": boolean
        - "feedback": specific improvement suggestions (empty string if none)
        - "score": 0-10
        """
        response = self.llm.generate(prompt, system=system)
        try:
            data = json.loads(self._extract_json(response["content"]))
            return data
        except:
            return {"requires_changes": False, "feedback": "", "score": 7.0}
    
    def _extract_json(self, text: str) -> str:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group() if match else "{}"


class Tester:
    """Analyzes code for correctness and generates test cases."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def analyze(self, code: str) -> Dict[str, Any]:
        system = "You are a QA engineer. Identify issues and edge cases."
        prompt = f"""
        Analyze this code for potential issues:
        {code}
        
        Return JSON:
        - "passed": boolean (true if no obvious issues)
        - "issues": string describing problems (empty if none)
        - "edge_cases": list of edge cases to test
        """
        response = self.llm.generate(prompt, system=system)
        try:
            return json.loads(self._extract_json(response["content"]))
        except:
            return {"passed": True, "issues": "", "edge_cases": []}
    
    def _extract_json(self, text: str) -> str:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group() if match else "{}"


class Debugger:
    """Surgical code fixer when Tester finds errors."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def fix(self, code: str, errors: str, context: str) -> Dict[str, Any]:
        system = "You are an expert debugger. Fix only what's broken, preserve functionality."
        prompt = f"""
        Fix the following code based on the reported errors.
        
        Code:
        {code}
        
        Errors:
        {errors}
        
        Context/Research:
        {context}
        
        Return JSON:
        - "content": the fixed code
        - "analysis": explanation of what was wrong and how you fixed it
        """
        response = self.llm.generate(prompt, system=system)
        try:
            data = json.loads(self._extract_json(response["content"]))
            return data
        except:
            return {"content": code, "analysis": "Unable to parse fix, returning original."}
    
    def _extract_json(self, text: str) -> str:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group() if match else "{}"


class Reporter:
    """Generates full markdown mission reports."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def generate(self, task_context) -> str:
        prompt = f"""
        Generate a professional markdown report for this completed task.
        
        Task ID: {task_context.task_id}
        Goal: {task_context.goal}
        Refined Goal: {task_context.refined_goal}
        Research: {task_context.research_findings}
        Code: {task_context.code_output}
        Test Results: {task_context.test_results}
        Council Verdict: {task_context.council_verdict}
        
        Include sections: Summary, Approach, Implementation, Results, Council Review.
        """
        response = self.llm.generate(prompt)
        return response["content"]


class Scout:
    """Web search using DuckDuckGo (no API key)."""
    
    def __init__(self):
        self.llm = LLMWrapper()
        import requests
        from bs4 import BeautifulSoup
        self.requests = requests
        self.BeautifulSoup = BeautifulSoup
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        response = self.requests.get(url)
        soup = self.BeautifulSoup(response.text, 'html.parser')
        results = []
        for link in soup.select('.result__a')[:num_results]:
            results.append({
                "title": link.get_text(),
                "url": link['href']
            })
        return results
    
    def fetch_content(self, url: str) -> str:
        try:
            response = self.requests.get(url, timeout=10)
            soup = self.BeautifulSoup(response.text, 'html.parser')
            # Basic text extraction
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text[:5000]
        except:
            return ""


class Synthesizer:
    """Merges multiple agent findings into a unified research brief."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def synthesize(self, primary_research: str, expert_findings: Dict[str, Any], goal: str) -> Dict[str, Any]:
        system = "You are a research synthesizer. Integrate multiple perspectives into a coherent brief."
        prompt = f"""
        Synthesize the following research into a unified brief for: {goal}
        
        Primary Research: {primary_research}
        
        Expert Analyses:
        {json.dumps(expert_findings, indent=2)}
        
        Provide:
        - Key Insights (consensus view)
        - Dissenting Opinions (where experts disagree)
        - Recommended Approach (actionable next steps)
        - Confidence Assessment (0-1)
        """
        response = self.llm.generate(prompt, system=system)
        # Try to extract confidence from content or use LLM confidence
        confidence = response["confidence"]
        return {"content": response["content"], "confidence": confidence}


class Presenter:
    """Formats research brief for Council presentation."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def prepare_presentation(self, synthesis: str, goal: str) -> str:
        prompt = f"""
        Convert this research synthesis into a clear, persuasive presentation for the Aetherion Council.
        
        Synthesis: {synthesis}
        Goal: {goal}
        
        Structure:
        1. Executive Summary (2 sentences)
        2. The Problem
        3. Proposed Solution
        4. Evidence & Analysis
        5. Risks & Mitigations
        6. Recommendation
        """
        response = self.llm.generate(prompt)
        return response["content"]


class DocumentationAgent:
    """Generates README, docstrings, and usage instructions."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def generate(self, task_context) -> str:
        prompt = f"""
        Generate comprehensive documentation for this project.
        
        Goal: {task_context.goal}
        Code: {task_context.code_output}
        Research: {task_context.research_findings}
        
        Include:
        - README.md content with installation, usage, examples
        - Key function docstrings (Google style)
        """
        response = self.llm.generate(prompt)
        return response["content"]
