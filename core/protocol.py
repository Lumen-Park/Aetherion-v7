"""
Aetherion Standard Inter‑Agent Protocol (SIP)
All communication between agents MUST use this format.

Includes:
- AgentMessage envelope
- LLMWrapper with confidence scoring and source comparison
- Priority and Verdict enums
- Message validation utilities
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import json
import time
import uuid
import re
import os

# Optional Ollama import
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: ollama not installed. LLM features will be disabled.")


class Priority(Enum):
    """Message priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


class Verdict(Enum):
    """Council voting verdicts."""
    APPROVE = "approve"
    REJECT = "reject"
    REVISION = "revision"
    ABSTAIN = "abstain"


@dataclass
class AgentMessage:
    """
    Standard envelope for all inter‑agent communication.
    
    Attributes:
        from_agent: Name of sending agent
        to_agent: Name of receiving agent (or 'broadcast')
        task_id: Unique task identifier
        priority: Message priority level
        payload: Message content as dictionary
        timestamp: Unix timestamp of creation
        message_id: UUID for tracing
        trace: List of agent names this message passed through
    """
    from_agent: str
    to_agent: str
    task_id: str
    priority: Priority = Priority.MEDIUM
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace: List[str] = field(default_factory=list)
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self), indent=2, default=str)
    
    @classmethod
    def from_json(cls, data: str) -> AgentMessage:
        """Deserialize from JSON string."""
        raw = json.loads(data)
        raw['priority'] = Priority(raw['priority'])
        return cls(**raw)
    
    def add_to_trace(self, agent_name: str) -> None:
        """Add an agent to the trace chain."""
        self.trace.append(agent_name)
    
    def create_reply(self, from_agent: str, payload: Dict[str, Any]) -> AgentMessage:
        """Create a reply message with proper trace."""
        new_trace = self.trace + [self.from_agent]
        return AgentMessage(
            from_agent=from_agent,
            to_agent=self.from_agent,
            task_id=self.task_id,
            priority=self.priority,
            payload=payload,
            trace=new_trace
        )


class LLMWrapper:
    """
    Unified interface to Ollama with confidence scoring and source comparison.
    Handles model loading, prompting, and response parsing.
    """
    
    def __init__(self, model: str = None, temperature: float = 0.7):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.temperature = temperature
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Verify Ollama is accessible."""
        if not OLLAMA_AVAILABLE:
            self.available = False
            return
        try:
            ollama.list()
            self.available = True
        except Exception as e:
            print(f"Warning: Ollama not accessible: {e}")
            self.available = False
    
    def generate(self, prompt: str, system: Optional[str] = None, 
                 model: Optional[str] = None, temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate a response with confidence estimation.
        
        Args:
            prompt: User prompt
            system: System prompt (optional)
            model: Override model (optional)
            temperature: Override temperature (optional)
        
        Returns:
            Dict with 'content', 'confidence', 'model', 'usage'
        """
        if not self.available:
            return self._mock_response(prompt)
        
        model_name = model or self.model
        temp = temperature if temperature is not None else self.temperature
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={"temperature": temp}
            )
            content = response["message"]["content"]
            confidence = self._estimate_confidence(content)
            
            return {
                "content": content,
                "confidence": confidence,
                "model": model_name,
                "usage": {
                    "eval_count": response.get("eval_count", 0),
                    "prompt_eval_count": response.get("prompt_eval_count", 0)
                }
            }
        except Exception as e:
            print(f"LLM generation error: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> Dict[str, Any]:
        """Fallback mock response when Ollama is unavailable."""
        return {
            "content": f"[MOCK RESPONSE] Unable to connect to Ollama. Prompt: {prompt[:100]}...",
            "confidence": 0.3,
            "model": "mock",
            "usage": {"eval_count": 0, "prompt_eval_count": 0}
        }
    
    def _estimate_confidence(self, text: str) -> float:
        """
        Heuristic confidence based on hedging language.
        Lower confidence when model uses uncertain language.
        """
        hedging_phrases = [
            "might", "could", "possibly", "maybe", "I think", "perhaps",
            "not sure", "uncertain", "likely", "probably", "may be"
        ]
        text_lower = text.lower()
        hedge_count = sum(1 for h in hedging_phrases if h in text_lower)
        # Inverse relationship: more hedging = lower confidence
        confidence = max(0.3, 1.0 - (hedge_count * 0.1))
        return min(0.95, confidence)
    
    def compare_sources(self, claims: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Given multiple sources on same topic, find top-3 consensus.
        
        Args:
            claims: List of dicts with 'source' and 'claim' keys
        
        Returns:
            Dict with 'consensus', 'top_3_sources', 'confidence'
        """
        prompt = f"""
        Analyze these sources and identify the consensus view.
        
        Sources:
        {json.dumps(claims, indent=2)}
        
        Return a JSON object with:
        - consensus: the agreed-upon facts (string)
        - top_3_sources: indices of the most reliable sources (list of ints)
        - confidence: 0-1 score for the consensus
        """
        response = self.generate(prompt)
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "consensus": None,
            "top_3_sources": list(range(min(3, len(claims)))),
            "confidence": 0.3
        }
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> Dict[str, Any]:
        """
        Multi-turn chat interface.
        
        Args:
            messages: List of {'role': 'user'/'assistant'/'system', 'content': str}
            model: Override model
        
        Returns:
            Same format as generate()
        """
        if not self.available:
            return self._mock_response(messages[-1]["content"])
        
        model_name = model or self.model
        try:
            response = ollama.chat(model=model_name, messages=messages)
            content = response["message"]["content"]
            confidence = self._estimate_confidence(content)
            return {
                "content": content,
                "confidence": confidence,
                "model": model_name,
                "usage": {"eval_count": response.get("eval_count", 0)}
            }
        except Exception as e:
            print(f"Chat error: {e}")
            return self._mock_response(messages[-1]["content"])
    
    def embed(self, text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
        """Generate embeddings for text."""
        if not self.available:
            return None
        try:
            response = ollama.embeddings(model=model, prompt=text)
            return response["embedding"]
        except:
            return None


class MessageValidator:
    """Utility to validate AgentMessage format."""
    
    @staticmethod
    def validate(message: AgentMessage) -> bool:
        """Check required fields."""
        required = ['from_agent', 'to_agent', 'task_id']
        for field in required:
            if not getattr(message, field, None):
                return False
        return True
    
    @staticmethod
    def is_valid_json(data: str) -> bool:
        """Check if string is valid AgentMessage JSON."""
        try:
            msg = AgentMessage.from_json(data)
            return MessageValidator.validate(msg)
        except:
            return False


class ProtocolRegistry:
    """
    Registry of message handlers for different agent types.
    Enables dynamic routing of messages.
    """
    
    def __init__(self):
        self.handlers: Dict[str, callable] = {}
    
    def register(self, agent_name: str, handler: callable) -> None:
        """Register a message handler for an agent."""
        self.handlers[agent_name] = handler
    
    def route(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Route a message to the appropriate handler."""
        handler = self.handlers.get(message.to_agent)
        if handler:
            return handler(message)
        return None
    
    def broadcast(self, message: AgentMessage, exclude: List[str] = None) -> Dict[str, Any]:
        """Send message to all registered agents except excluded ones."""
        exclude = exclude or []
        results = {}
        for agent_name, handler in self.handlers.items():
            if agent_name not in exclude:
                msg_copy = AgentMessage(
                    from_agent=message.from_agent,
                    to_agent=agent_name,
                    task_id=message.task_id,
                    priority=message.priority,
                    payload=message.payload.copy(),
                    trace=message.trace + [message.from_agent]
                )
                results[agent_name] = handler(msg_copy)
        return results


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Priority",
    "Verdict",
    "AgentMessage",
    "LLMWrapper",
    "MessageValidator",
    "ProtocolRegistry"
            ]
