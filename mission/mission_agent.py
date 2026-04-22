import json
import os
import time
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from core.protocol import LLMWrapper


class ScoutAgent:
    def __init__(self):
        self.llm = LLMWrapper()

    def search_github_issues(
        self, query: str, language: str = "python", limit: int = 10
    ) -> List[Dict]:
        url = f"https://api.github.com/search/issues?q={query}+language:{language}+state:open&per_page={limit}"
        resp = requests.get(url)
        if resp.status_code == 200:
            return [
                {
                    "title": i["title"],
                    "body": i["body"],
                    "url": i["html_url"],
                    "repo": i["repository_url"].split("/")[-1],
                    "labels": [l["name"] for l in i["labels"]],
                }
                for i in resp.json().get("items", [])
            ]
        return []

    def search_web(self, query: str) -> List[str]:
        soup = BeautifulSoup(
            requests.get(f"https://html.duckduckgo.com/html/?q={query}").text,
            "html.parser",
        )
        return [a["href"] for a in soup.select(".result__a")[:5]]


class FilterAgent:
    def __init__(self):
        self.llm = LLMWrapper()

    def filter_issues(self, issues: List[Dict]) -> List[Dict]:
        filtered = []
        for issue in issues:
            prompt = f"Evaluate if this GitHub issue is suitable for an AI to solve:\nTitle: {issue['title']}\nBody: {issue.get('body','')}\nReturn JSON: {{'suitable': bool, 'reason': str}}"
            resp = self.llm.generate(prompt)
            try:
                if json.loads(resp["content"]).get("suitable"):
                    filtered.append(issue)
            except:
                pass
        return filtered


class SelectorAgent:
    def __init__(self):
        self.llm = LLMWrapper()

    def select_best(self, issues: List[Dict]) -> Optional[Dict]:
        if not issues:
            return None
        prompt = f"Rank these issues by suitability for an AI agent:\n{json.dumps(issues, indent=2)}\nReturn JSON: {{'selected_index': 0}}"
        resp = self.llm.generate(prompt)
        try:
            return issues[json.loads(resp["content"]).get("selected_index", 0)]
        except:
            return issues[0]


class GitPayloadBuilder:
    def __init__(self):
        self.llm = LLMWrapper()

    def build_payload(
        self, issue: Dict, solution_code: str, explanation: str
    ) -> Dict:
        commit_msg = f"Fix: {issue['title']}\n\n{explanation}"
        payload = {
            "issue_url": issue["url"],
            "commit_message": commit_msg,
            "patch": solution_code,
            "explanation": explanation,
        }
        os.makedirs("./git_payloads", exist_ok=True)
        with open(
            os.path.join("./git_payloads", f"payload_{int(time.time())}.json"),
            "w",
        ) as f:
            json.dump(payload, f, indent=2)
        return payload
