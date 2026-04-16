"""
Mission Agent – Scout open issues, filter, solve, and prepare git payload.
"""

import json
import requests
from typing import List, Dict, Optional
from core.protocol import LLMWrapper
from bs4 import BeautifulSoup

class ScoutAgent:
    """Finds open issues from GitHub and forums."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def search_github_issues(self, query: str, language: str = "python", limit: int = 10) -> List[Dict]:
        # Use GitHub API (no auth needed for public repos)
        url = f"https://api.github.com/search/issues?q={query}+language:{language}+state:open&per_page={limit}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            issues = []
            for item in data.get('items', []):
                issues.append({
                    "title": item['title'],
                    "body": item['body'],
                    "url": item['html_url'],
                    "repo": item['repository_url'].split('/')[-1],
                    "labels": [l['name'] for l in item['labels']]
                })
            return issues
        return []
    
    def search_web(self, query: str) -> List[str]:
        # DuckDuckGo search
        url = f"https://html.duckduckgo.com/html/?q={query}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = [a['href'] for a in soup.select('.result__a')[:5]]
        return results

class FilterAgent:
    """Removes issues that are too large, vague, or unsafe."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def filter_issues(self, issues: List[Dict]) -> List[Dict]:
        filtered = []
        for issue in issues:
            prompt = f"""
            Evaluate if this GitHub issue is suitable for an AI to solve:
            Title: {issue['title']}
            Body: {issue.get('body', '')}
            
            Return JSON: {{"suitable": bool, "reason": str}}
            """
            response = self.llm.generate(prompt)
            try:
                result = json.loads(response['content'])
                if result.get('suitable'):
                    filtered.append(issue)
            except:
                pass
        return filtered

class SelectorAgent:
    """Picks the best task based on difficulty and clarity."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def select_best(self, issues: List[Dict]) -> Optional[Dict]:
        if not issues:
            return None
        prompt = f"""
        Rank these issues by suitability for an AI agent (difficulty 2-4/10, clear requirements):
        {json.dumps(issues, indent=2)}
        
        Return JSON: {{"selected_index": 0}}
        """
        response = self.llm.generate(prompt)
        try:
            data = json.loads(response['content'])
            idx = data.get('selected_index', 0)
            return issues[idx]
        except:
            return issues[0]

class GitPayloadBuilder:
    """Prepares patch and commit message for human approval."""
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def build_payload(self, issue: Dict, solution_code: str, explanation: str) -> Dict:
        commit_msg = f"Fix: {issue['title']}\n\n{explanation}"
        payload = {
            "issue_url": issue['url'],
            "commit_message": commit_msg,
            "patch": solution_code,  # In production, generate proper diff
            "explanation": explanation
        }
        # Save for human review
        os.makedirs("./git_payloads", exist_ok=True)
        filename = f"payload_{int(time.time())}.json"
        with open(os.path.join("./git_payloads", filename), 'w') as f:
            json.dump(payload, f, indent=2)
        return payload
