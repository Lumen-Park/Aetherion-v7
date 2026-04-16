"""
Aetherion Standard Inter‑Agent Protocol (SIP)
All communication between agents MUST use this format.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum
import json
import time
import uuid
import ollama

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"

class Verdict(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REVISION = "revision"
    ABSTAIN = "abstain"

@dataclass
class AgentMessage:
    """Standard envelope for all inter‑agent communication."""
    from_agent: str
    to_agent: str
    task_id: str
    priority: Priority = Priority.MEDIUM
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace: List[str] = field(default_factory=list)  # agent chain
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, default=str)
    
    @classmethod
    def from_json(cls, data: str) -> AgentMessage:
        return cls(**json.loads(data))

class LLMWrapper:
    """Unified interface to Ollama with confidence scoring and source comparison."""
    
    def __init__(self, model: str = "llama3", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
    
    def generate(self, prompt: str, system: Optional[str] = None) -> Dict[str, Any]:
        """Generate a response with confidence estimation."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options={"temperature": self.temperature}
        )
        
        content = response["message"]["content"]
        confidence = self._estimate_confidence(content)
        
        return {
            "content": content,
            "confidence": confidence,
            "model": self.model,
            "usage": response.get("eval_count", 0)
        }
    
    def _estimate_confidence(self, text: str) -> float:
        """Heuristic confidence based on hedging language."""
        hedging = ["might", "could", "possibly", "maybe", "I think", "perhaps"]
        text_lower = text.lower()
        hedge_count = sum(1 for h in hedging if h in text_lower)
        # Simple inverse relationship
        return max(0.1, 1.0 - (hedge_count * 0.15))
    
    def compare_sources(self, claims: List[Dict[str, str]]) -> Dict[str, Any]:
        """Given multiple sources on same topic, find top-3 consensus."""
        prompt = f"""
        Analyze these sources and identify the consensus view.
        Return JSON with:
        - consensus: the agreed-upon facts
        - top_3_sources: list of most reliable source indices
        - confidence: 0-1 score
        
        Sources:
        {json.dumps(claims, indent=2)}
        """
        response = self.generate(prompt)
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"consensus": None, "top_3_sources": [], "confidence": 0.0}
