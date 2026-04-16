"""
Aetherion Council – 7‑judge panel with pre/post pipeline.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from core.protocol import LLMWrapper, Verdict

@dataclass
class JudgeVote:
    agent: str
    verdict: Verdict
    confidence: float
    score: float
    reasoning: str

class AetherionCouncil:
    """7‑judge Supreme Council with absolute Security veto."""
    
    def __init__(self):
        self.llm = LLMWrapper()
        self.judges = [
            "Critic", "Security", "Alignment", "Constraint",
            "Evaluator", "Documentation", "AetherionPrime"
        ]
        self.veto_judges = ["Security"]
    
    def deliberate(self, output: str, original_goal: str) -> Dict[str, Any]:
        """Run full council pipeline."""
        # Pre‑council
        sanitized = self._sanitize(output)
        forensic = self._forensic_check(sanitized)
        edge_cases = self._generate_edge_cases(sanitized)
        
        # Voting
        votes = self._collect_votes(sanitized, original_goal, forensic, edge_cases)
        
        # Bias detection
        bias_flag = self._detect_bias(votes)
        
        # Security veto check
        for vote in votes:
            if vote.agent == "Security" and vote.verdict == Verdict.REJECT:
                return {
                    "verdict": "REJECTED",
                    "reason": "Security absolute veto",
                    "votes": [v.__dict__ for v in votes],
                    "bias_detected": bias_flag
                }
        
        # Majority decision
        approve_count = sum(1 for v in votes if v.verdict == Verdict.APPROVE)
        verdict = "APPROVED" if approve_count >= 5 else "REVISION_REQUIRED" if approve_count >= 4 else "REJECTED"
        
        avg_score = sum(v.score for v in votes) / len(votes)
        
        return {
            "verdict": verdict,
            "score": avg_score,
            "votes": [v.__dict__ for v in votes],
            "bias_detected": bias_flag,
            "forensic_report": forensic,
            "edge_cases": edge_cases
        }
    
    def _sanitize(self, text: str) -> str:
        prompt = "Remove all markdown and conversational filler. Return only the core technical content."
        return self.llm.generate(prompt, system="You are a sanitizer.")["content"]
    
    def _forensic_check(self, text: str) -> Dict:
        prompt = f"Fact‑check this: {text}. Verify imports, APIs, resource requirements."
        response = self.llm.generate(prompt)
        return {"findings": response["content"], "confidence": response["confidence"]}
    
    def _generate_edge_cases(self, text: str) -> List[str]:
        prompt = f"Generate 3 adversarial edge cases for: {text}"
        response = self.llm.generate(prompt)
        return response["content"].split("\n")[:3]
    
    def _collect_votes(self, output: str, goal: str, forensic: Dict, edge_cases: List) -> List[JudgeVote]:
        votes = []
        for judge in self.judges:
            prompt = self._judge_prompt(judge, output, goal, forensic, edge_cases)
            response = self.llm.generate(prompt)
            # Parse JSON from response (simplified)
            vote_data = self._parse_vote(response["content"])
            vote_data["agent"] = judge
            votes.append(JudgeVote(**vote_data))
        return votes
    
    def _judge_prompt(self, judge: str, output: str, goal: str, forensic: Dict, edge_cases: List) -> str:
        prompts = {
            "Critic": "Find the strongest argument against this output.",
            "Security": "Identify any security vulnerabilities or unsafe patterns. Be strict.",
            "Alignment": "Does this output exactly match the user's request?",
            "Constraint": "Is this within scope and resource limits?",
            "Evaluator": "Score quality 0-10. Is reasoning sound?",
            "Documentation": "Can a stranger understand this?",
            "AetherionPrime": "Given split votes, what is the safest path?"
        }
        return f"""
        As {judge}, {prompts[judge]}
        
        Output: {output}
        Original Goal: {goal}
        Forensic Report: {forensic}
        Edge Cases: {edge_cases}
        
        Return JSON: {{"verdict": "approve/reject/abstain", "confidence": 0.X, "score": 0.X, "reasoning": "..."}}
        """
    
    def _parse_vote(self, text: str) -> Dict:
        import json, re
        try:
            # Extract JSON block
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return {
                    "verdict": Verdict(data.get("verdict", "abstain").lower()),
                    "confidence": float(data.get("confidence", 0.5)),
                    "score": float(data.get("score", 5.0)),
                    "reasoning": data.get("reasoning", "")
                }
        except:
            pass
        return {"verdict": Verdict.ABSTAIN, "confidence": 0.5, "score": 5.0, "reasoning": "Parse error"}
    
    def _detect_bias(self, votes: List[JudgeVote]) -> bool:
        # Simple heuristic: all scores within 0.5 of mean → possible groupthink
        scores = [v.score for v in votes]
        avg = sum(scores) / len(scores)
        return all(abs(s - avg) < 0.5 for s in scores)
