"""
Aetherion Council – 7-judge Supreme Court with full pre/post pipeline.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from core.protocol import LLMWrapper, Verdict


@dataclass
class JudgeVote:
    agent: str
    verdict: Verdict
    confidence: float
    score: float
    reasoning: str


class SanitizerAgent:
    def __init__(self):
        self.llm = LLMWrapper()

    def clean(self, text: str) -> str:
        prompt = f"""
        Remove all markdown formatting, conversational filler, and extraneous text.
        Return ONLY the core technical content, code, or research findings.

        Input: {text}
        """
        response = self.llm.generate(
            prompt, system="You are a content sanitizer."
        )
        return response["content"]


class ForensicAnalyst:
    def __init__(self):
        self.llm = LLMWrapper()

    def analyze(self, text: str) -> Dict[str, Any]:
        prompt = f"""
        Perform a forensic analysis on this output:
        {text}

        Check:
        1. Are all imports standard library or well-known packages?
        2. Are referenced APIs likely real and accessible?
        3. Are resource requirements (CPU, RAM) reasonable for a laptop?
        4. Are there any factual claims that need verification?

        Return JSON:
        - "issues": list of potential problems
        - "verified": boolean (true if passes basic checks)
        - "confidence": 0-1
        """
        response = self.llm.generate(prompt)
        try:
            return json.loads(self._extract_json(response["content"]))
        except Exception:
            return {"issues": [], "verified": True, "confidence": 0.5}

    def _extract_json(self, text: str) -> str:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return match.group() if match else "{}"


class EdgeCaseGenerator:
    def __init__(self):
        self.llm = LLMWrapper()

    def generate(self, text: str) -> List[str]:
        prompt = f"""
        Based on this output, generate 3-5 specific edge cases or adversarial inputs
        that could break the solution or reveal weaknesses.

        Output: {text}

        Return a JSON list of strings, each describing an edge case.
        """
        response = self.llm.generate(prompt)
        try:
            return json.loads(self._extract_json(response["content"]))
        except Exception:
            return [
                "Empty input",
                "Very large input",
                "Negative numbers where not expected",
            ]

    def _extract_json(self, text: str) -> str:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        return match.group() if match else "[]"


class Juror:
    def __init__(self):
        self.llm = LLMWrapper()

    def detect_bias(self, votes: List[JudgeVote]) -> Dict[str, Any]:
        scores = [v.score for v in votes]
        avg = sum(scores) / len(scores) if scores else 0
        variance = (
            sum((s - avg) ** 2 for s in scores) / len(scores) if scores else 0
        )

        flags = []
        if variance < 0.5:
            flags.append("possible_groupthink")
        if all(v.verdict == Verdict.APPROVE for v in votes):
            flags.append("unanimous_approval_bias")

        votes_serializable = []
        for v in votes:
            v_dict = v.__dict__.copy()
            v_dict["verdict"] = v_dict["verdict"].value
            votes_serializable.append(v_dict)

        prompt = f"""
        Analyze these council votes for cognitive biases:
        {json.dumps(votes_serializable, indent=2)}

        Identify: groupthink, anchoring, complexity bias, confirmation bias.
        Return JSON with "flags" list and "analysis" string.
        """
        response = self.llm.generate(prompt)
        try:
            llm_flags = json.loads(self._extract_json(response["content"]))
            flags.extend(llm_flags.get("flags", []))
            analysis = llm_flags.get("analysis", "")
        except Exception:
            analysis = ""

        return {"flags": flags, "analysis": analysis}

    def _extract_json(self, text: str) -> str:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return match.group() if match else "{}"


class Liaison:
    def format_verdict(self, verdict: Dict) -> str:
        v = verdict.get("verdict", "UNKNOWN")
        score = verdict.get("score", 0)
        bias = verdict.get("bias_detected", False)

        if v == "REJECTED":
            symbol = "❌"
            explanation = "Council rejected this output."
        elif v == "APPROVED":
            symbol = "✅"
            explanation = "Council approved this output."
        else:
            symbol = "⚠️"
            explanation = "Council requires revisions."

        bias_note = "\n⚠️ Bias detected in deliberation." if bias else ""
        return f"{symbol} Council Verdict: {v} (Score: {score:.2f})\n{explanation}{bias_note}"


class Telemetry:
    def __init__(self):
        self.history = []

    def record_verdict(self, verdict: Dict):
        self.history.append(
            {
                "timestamp": __import__("time").time(),
                "verdict": verdict.get("verdict"),
                "score": verdict.get("score"),
            }
        )

    def get_stats(self) -> Dict:
        if not self.history:
            return {"approval_rate": 0, "avg_score": 0}
        approves = sum(1 for h in self.history if h["verdict"] == "APPROVED")
        avg_score = sum(h["score"] for h in self.history) / len(self.history)
        return {
            "total": len(self.history),
            "approval_rate": approves / len(self.history),
            "avg_score": avg_score,
        }


class AetherionCouncil:
    """7-judge Supreme Council with absolute Security veto."""

    def __init__(self):
        self.llm = LLMWrapper()
        self.sanitizer = SanitizerAgent()
        self.forensic = ForensicAnalyst()
        self.edge_gen = EdgeCaseGenerator()
        self.juror = Juror()
        self.liaison = Liaison()
        self.telemetry = Telemetry()

        self.judges = [
            "Critic",
            "Security",
            "Alignment",
            "Constraint",
            "Evaluator",
            "Documentation",
            "AetherionPrime",
        ]
        self.veto_judges = ["Security"]

    def deliberate(
        self,
        output: str,
        original_goal: str,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Run full council pipeline with optional weighted voting."""
        sanitized = self.sanitizer.clean(output)
        forensic = self.forensic.analyze(sanitized)
        edge_cases = self.edge_gen.generate(sanitized)

        votes = self._collect_votes(
            sanitized, original_goal, forensic, edge_cases
        )
        bias_info = self.juror.detect_bias(votes)

        # Security veto
        for vote in votes:
            if vote.agent == "Security" and vote.verdict == Verdict.REJECT:
                verdict_result = {
                    "verdict": "REJECTED",
                    "reason": "Security absolute veto",
                    "votes": self._serialize_votes(votes),
                    "bias_detected": bool(bias_info["flags"]),
                    "forensic_report": forensic,
                    "edge_cases": edge_cases,
                    "score": 0.0,
                }
                self.telemetry.record_verdict(verdict_result)
                return verdict_result

        # Weighted or simple average
        if weights:
            weighted_sum = 0.0
            total_weight = 0.0
            for vote in votes:
                w = weights.get(vote.agent, 1.0)
                weighted_sum += vote.score * w
                total_weight += w
            avg_score = (
                weighted_sum / total_weight if total_weight > 0 else 5.0
            )
        else:
            avg_score = sum(v.score for v in votes) / len(votes)

        # Verdict based on weighted average score
        if avg_score >= 7.0:
            verdict_str = "APPROVED"
        elif avg_score >= 5.0:
            verdict_str = "REVISION_REQUIRED"
        else:
            verdict_str = "REJECTED"

        verdict_result = {
            "verdict": verdict_str,
            "score": avg_score,
            "votes": self._serialize_votes(votes),
            "bias_detected": bool(bias_info["flags"]),
            "bias_analysis": bias_info.get("analysis", ""),
            "forensic_report": forensic,
            "edge_cases": edge_cases,
        }
        self.telemetry.record_verdict(verdict_result)
        return verdict_result

    def _serialize_votes(self, votes: List[JudgeVote]) -> List[Dict]:
        result = []
        for v in votes:
            v_dict = v.__dict__.copy()
            v_dict["verdict"] = v_dict["verdict"].value
            result.append(v_dict)
        return result

    def _collect_votes(
        self, output: str, goal: str, forensic: Dict, edge_cases: List
    ) -> List[JudgeVote]:
        votes = []
        for judge in self.judges:
            prompt = self._judge_prompt(
                judge, output, goal, forensic, edge_cases
            )
            response = self.llm.generate(prompt)
            votes.append(self._parse_vote(response["content"], judge))
        return votes

    def _judge_prompt(
        self,
        judge: str,
        output: str,
        goal: str,
        forensic: Dict,
        edge_cases: List,
    ) -> str:
        prompts = {
            "Critic": "Find the strongest argument against this output. Be skeptical.",
            "Security": "Identify any security vulnerabilities, unsafe patterns, or exposed secrets. Be strict. REJECT if any found.",
            "Alignment": "Does this output exactly match the user's original request? Flag any deviation.",
            "Constraint": "Is this within reasonable scope and resource limits? Flag over-engineering.",
            "Evaluator": "Score overall quality 0-10. Consider correctness, efficiency, readability.",
            "Documentation": "Can a stranger understand and use this output? Is it well-documented?",
            "AetherionPrime": "Given all perspectives, what is the safest and most reasonable path forward?",
        }
        return f"""
        As the {judge} on the Aetherion Council, evaluate this output.
        {prompts[judge]}

        Output: {output}
        Original Goal: {goal}
        Forensic Report: {json.dumps(forensic)}
        Edge Cases: {json.dumps(edge_cases)}

        Return a JSON object with:
        - "verdict": "approve", "reject", or "abstain"
        - "confidence": 0.0 to 1.0
        - "score": 0.0 to 10.0
        - "reasoning": brief explanation
        """

    def _parse_vote(self, content: str, judge_name: str) -> JudgeVote:
        try:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                data = json.loads(match.group())
                verdict_str = data.get("verdict", "abstain").lower()
                if verdict_str == "approve":
                    verdict = Verdict.APPROVE
                elif verdict_str == "reject":
                    verdict = Verdict.REJECT
                else:
                    verdict = Verdict.ABSTAIN
                return JudgeVote(
                    agent=judge_name,
                    verdict=verdict,
                    confidence=float(data.get("confidence", 0.5)),
                    score=float(data.get("score", 5.0)),
                    reasoning=data.get("reasoning", ""),
                )
        except Exception:
            pass
        return JudgeVote(
            agent=judge_name,
            verdict=Verdict.ABSTAIN,
            confidence=0.5,
            score=5.0,
            reasoning="Parse error",
        )
