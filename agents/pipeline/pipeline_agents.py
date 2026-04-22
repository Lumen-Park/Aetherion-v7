"""
Pipeline Agents – Researcher, Developer, Partner, Tester, Reporter,
Scout, Synthesizer, Presenter, GoalRefiner, DocumentationAgent, Debugger.
"""

import json
import re
from typing import Dict, Any, List
from core.protocol import LLMWrapper


class GoalRefiner:
    def __init__(self):
        self.llm = LLMWrapper()

    def refine(self, goal: str) -> Dict[str, Any]:
        prompt = (
            f"Refine this vague goal into a precise, actionable task.\n"
            f"Original: {goal}\n"
            f"Return JSON with refined_goal, subtasks, success_criteria."
        )
        response = self.llm.generate(prompt)
        try:
            data = json.loads(self._extract_json(response["content"]))
            return {
                "content": data.get("refined_goal", goal),
                "confidence": response["confidence"]
            }
        except Exception:
            return {"content": goal, "confidence": 0.5}

    def _extract_json(self, text: str) -> str:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group() if match else "{}"


class Researcher:
    def __init__(self):
        self.llm = LLMWrapper()

    def execute(self, query: str, context: str = "") -> Dict[str, Any]:
        system = (
            "You are a senior researcher. Provide thorough, evidence-based "
            "analysis with citations."
        )
        prompt = f"Research thoroughly:\n{query}\n\nContext: {context}"
        response = self.llm.generate(prompt, system=system)
        return {"content": response["content"], "confidence": response["confidence"]}


class Developer:
    def __init__(self):
        self.llm = LLMWrapper()

    def write_code(self, research: str, goal: str, strategy_hint: str = "") -> Dict[str, Any]:
        system = (
            "You are an expert Python developer. Write clean, well-documented, "
            "production-ready code."
        )
        prompt = (
            f"Write code to accomplish: {goal}\n\n"
            f"Research findings: {research}\n"
            f"Strategy hint: {strategy_hint}\n"
            f"Return ONLY the Python code block."
        )
        response = self.llm.generate(prompt, system=system)
        code = self._extract_code(response["content"])
        return {"content": code, "confidence": response["confidence"]}

    def _extract_code(self, text: str) -> str:
        match = re.search(r'```python(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        match = re.search(r'```(.*?)```', text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()


class Partner:
    def __init__(self):
        self.llm = LLMWrapper()

    def review(self, code: str, goal: str) -> Dict[str, Any]:
        system = "You are a senior code reviewer. Be thorough but constructive."
        prompt = (
            f"Review this code against the original goal: {goal}\n\n"
            f"Code:\n{code}\n"
            f"Return JSON: requires_changes (bool), feedback (string), score (0-10)."
        )
        response = self.llm.generate(prompt, system=system)
        try:
            return json.loads(self._extract_json(response["content"]))
        except Exception:
            return {"requires_changes": False, "feedback": "", "score": 7.0}

    def _extract_json(self, text: str) -> str:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group() if match else "{}"


class Tester:
    def __init__(self):
        self.llm = LLMWrapper()

    def analyze(self, code: str) -> Dict[str, Any]:
        system = "You are a QA engineer. Identify issues and edge cases."
        prompt = (
            f"Analyze this code for potential issues:\n{code}\n"
            f"Return JSON: passed (bool), issues (string), edge_cases (list)."
        )
        response = self.llm.generate(prompt, system=system)
        try:
            return json.loads(self._extract_json(response["content"]))
        except Exception:
            return {"passed": True, "issues": "", "edge_cases": []}

    def _extract_json(self, text: str) -> str:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group() if match else "{}"


class Debugger:
    def __init__(self):
        self.llm = LLMWrapper()

    def fix(self, code: str, errors: str, context: str) -> Dict[str, Any]:
        system = "You are an expert debugger. Fix only what's broken, preserve functionality."
        prompt = (
            f"Fix the following code based on the reported errors.\n\n"
            f"Code:\n{code}\n\nErrors:\n{errors}\n\nContext:\n{context}\n"
            f"Return JSON: content (fixed code), analysis (explanation)."
        )
        response = self.llm.generate(prompt, system=system)
        try:
            return json.loads(self._extract_json(response["content"]))
        except Exception:
            return {"content": code, "analysis": "Parse error, returning original."}

    def _extract_json(self, text: str) -> str:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group() if match else "{}"


class Reporter:
    def __init__(self):
        self.llm = LLMWrapper()

    def generate(self, task_context) -> str:
        prompt = (
            f"Generate a professional markdown report.\n"
            f"Task: {task_context.goal}\nRefined: {task_context.refined_goal}\n"
            f"Research: {task_context.research_findings}\n"
            f"Code: {task_context.code_output}\n"
            f"Tests: {task_context.test_results}\n"
            f"Council: {task_context.council_verdict}"
        )
        return self.llm.generate(prompt)["content"]


class Scout:
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
            results.append({"title": link.get_text(), "url": link['href']})
        return results

    def fetch_content(self, url: str) -> str:
        try:
            response = self.requests.get(url, timeout=10)
            soup = self.BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return '\n'.join(chunk for chunk in chunks if chunk)[:5000]
        except Exception:
            return ""


class Synthesizer:
    def __init__(self):
        self.llm = LLMWrapper()

    def synthesize(
        self, primary_research: str, expert_findings: Dict[str, Any], goal: str
    ) -> Dict[str, Any]:
        system = "You are a research synthesizer."
        prompt = (
            f"Synthesize research for: {goal}\n"
            f"Primary: {primary_research}\n"
            f"Expert Analyses: {json.dumps(expert_findings, indent=2)}"
        )
        response = self.llm.generate(prompt, system=system)
        return {"content": response["content"], "confidence": response["confidence"]}


class Presenter:
    def __init__(self):
        self.llm = LLMWrapper()

    def prepare_presentation(self, synthesis: str, goal: str) -> str:
        prompt = (
            f"Convert this research synthesis into a clear presentation for the "
            f"Aetherion Council.\nSynthesis: {synthesis}\nGoal: {goal}"
        )
        return self.llm.generate(prompt)["content"]


class DocumentationAgent:
    def __init__(self):
        self.llm = LLMWrapper()

    def generate(self, task_context) -> str:
        prompt = (
            f"Generate comprehensive documentation.\n"
            f"Goal: {task_context.goal}\nCode: {task_context.code_output}\n"
            f"Research: {task_context.research_findings}"
        )
        return self.llm.generate(prompt)["content"]
