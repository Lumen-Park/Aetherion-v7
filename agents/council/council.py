"""
Aetherion Council – 7-judge Supreme Court with full pre/post pipeline.
Supports custom constitutions and weighted voting.
"""

import json
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from core.protocol import (LLMWrapper, Verdict, _extract_json_array,
                           _extract_json_object)


@dataclass
class JudgeVote:
    agent: str
    verdict: Verdict
    confidence: float
    score: float
    reasoning: str


class SanitizerAgent:
    def __init__(self, llm: LLMWrapper):
        self.llm = llm

    def clean(self, text: str) -> str:
        prompt = f"""
        Remove all markdown formatting, conversational filler, and extraneous text.
        Return ONLY the core technical content, code, or research findings.

        Input: {text}
        """
        response = self.llm.generate(
            prompt, system="You are a content sanitizer."
        )
        if response.get("mock"):
            return text
        return response["content"]


class ForensicAnalyst:
    def __init__(self, llm: LLMWrapper):
        self.llm = llm

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
        if response.get("mock"):
            return {
                "issues": [],
                "verified": False,
                "confidence": 0.0,
                "mock": True,
            }
        try:
            return json.loads(_extract_json_object(response["content"]))
        except Exception:
            return {"issues": [], "verified": True, "confidence": 0.5}


class EdgeCaseGenerator:
    def __init__(self, llm: LLMWrapper):
        self.llm = llm

    def generate(self, text: str) -> List[str]:
        prompt = f"""
        Based on this output, generate 3-5 specific edge cases or adversarial inputs
        that could break the solution or reveal weaknesses.

        Output: {text}

        Return a JSON list of strings, each describing an edge case.
        """
        response = self.llm.generate(prompt)
        if response.get("mock"):
            return []
        try:
            return json.loads(_extract_json_array(response["content"]))
        except Exception:
            return [
                "Empty input",
                "Very large input",
                "Negative numbers where not expected",
            ]


class Juror:
    def __init__(self, llm: LLMWrapper):
        self.llm = llm

    def detect_bias(self, votes: List[JudgeVote]) -> Dict[str, Any]:
        if not votes:
            return {"flags": ["no_votes"], "analysis": "No votes were cast."}

        scores = [v.score for v in votes]
        avg = sum(scores) / len(scores)
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)

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
        if response.get("mock"):
            return {
                "flags": flags,
                "analysis": "Bias analysis unavailable (Ollama offline).",
            }
        try:
            llm_result = json.loads(_extract_json_object(response["content"]))
            all_flags = list(set(flags + llm_result.get("flags", [])))
            analysis = llm_result.get("analysis", "")
        except Exception:
            all_flags = flags
            analysis = ""

        return {"flags": all_flags, "analysis": analysis}


class Liaison:
    def format_verdict(self, verdict: Dict) -> str:
        v = verdict.get("verdict", "UNKNOWN")
        score = verdict.get("score", 0)
        bias = verdict.get("bias_detected", False)
        mock = verdict.get("mock_run", False)

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
        mock_note = (
            "\n🔶 WARNING: Ollama was unavailable. This verdict is based on mock data and should not be trusted."
            if mock
            else ""
        )
        return f"{symbol} Council Verdict: {v} (Score: {score:.2f})\n{explanation}{bias_note}{mock_note}"


class Telemetry:
    def __init__(self):
        self.history = []

    def record_verdict(self, verdict: Dict):
        self.history.append(
            {
                "timestamp": time.time(),
                "verdict": verdict.get("verdict"),
                "score": verdict.get("score") or 0.0,
            }
        )

    def get_stats(self) -> Dict:
        if not self.history:
            return {"total": 0, "approval_rate": 0, "avg_score": 0}
        approves = sum(1 for h in self.history if h["verdict"] == "APPROVED")
        scores = [h["score"] for h in self.history if h["score"] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return {
            "total": len(self.history),
            "approval_rate": approves / len(self.history),
            "avg_score": avg_score,
        }


class AetherionCouncil:
    """7-judge Supreme Council with absolute Security veto."""

    def __init__(self, llm: Optional[LLMWrapper] = None):
        self.llm = llm or LLMWrapper()
        self.sanitizer = SanitizerAgent(self.llm)
        self.forensic = ForensicAnalyst(self.llm)
        self.edge_gen = EdgeCaseGenerator(self.llm)
        self.juror = Juror(self.llm)
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
        constitution: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Run full council pipeline with optional custom constitution."""
        if not self.llm.available:
            raise RuntimeError(
                "Ollama is not available. Cannot run council deliberation. "
                "Start Ollama or set AETHERION_TEST_MODE=true to use mock mode."
            )

        sanitized = self.sanitizer.clean(output)
        forensic = self.forensic.analyze(sanitized)
        edge_cases = self.edge_gen.generate(sanitized)

        # Use provided constitution or fall back to defaults
        if constitution:
            thresholds = constitution.get(
                "thresholds", {"approved": 7.0, "revision": 5.0}
            )
            custom_judges = constitution.get("judges", {})
        else:
            thresholds = {"approved": 7.0, "revision": 5.0}
            custom_judges = {}

        votes = self._collect_votes(
            sanitized,
            original_goal,
            forensic,
            edge_cases,
            custom_judges=custom_judges,
        )

        if not votes:
            raise RuntimeError(
                "No votes were collected. Council cannot deliberate."
            )

        bias_info = self.juror.detect_bias(votes)

        # Security veto (only if Security judge is enabled and votes REJECT/REVISION)
        for vote in votes:
            if vote.agent == "Security" and vote.verdict in (
                Verdict.REJECT,
                Verdict.REVISION,
            ):
                verdict_result = {
                    "verdict": "REJECTED",
                    "reason": f"Security absolute veto (Security voted {vote.verdict.value})",
                    "security_reasoning": vote.reasoning,
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

        # Use custom thresholds
        if avg_score >= thresholds["approved"]:
            verdict_str = "APPROVED"
        elif avg_score >= thresholds["revision"]:
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
        self,
        output: str,
        goal: str,
        forensic: Dict,
        edge_cases: List,
        custom_judges: Optional[Dict] = None,
    ) -> List[JudgeVote]:
        """Collect votes from enabled judges using custom prompts if provided."""
        votes = []
        for judge in self.judges:
            judge_config = (
                custom_judges.get(judge, {}) if custom_judges else {}
            )
            if not judge_config.get("enabled", True):
                continue  # Skip disabled judges

            # Use custom prompt if provided, otherwise use default
            if "prompt" in judge_config:
                prompt = (
                    judge_config["prompt"]
                    + f"\n\nOutput: {output}\nOriginal Goal: {goal}\nForensic Report: {json.dumps(forensic)}\nEdge Cases: {json.dumps(edge_cases)}\n\nReturn JSON with verdict, confidence, score, reasoning."
                )
            else:
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
            "Security": (
                "Identify any security vulnerabilities, unsafe patterns, or exposed secrets. "
                "Be strict. Use 'reject' if critical issues are found, 'revision' for minor concerns."
            ),
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
        - "verdict": "approve", "reject", "revision", or "abstain"
        - "confidence": 0.0 to 1.0
        - "score": 0.0 to 10.0
        - "reasoning": brief explanation
        """

    def _parse_vote(self, content: str, judge_name: str) -> JudgeVote:
        try:
            extracted = _extract_json_object(content)
            if extracted != "{}":
                data = json.loads(extracted)
                verdict_str = data.get("verdict", "abstain").lower()
                if verdict_str == "approve":
                    verdict = Verdict.APPROVE
                elif verdict_str == "reject":
                    verdict = Verdict.REJECT
                elif verdict_str == "revision":
                    verdict = Verdict.REVISION
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
