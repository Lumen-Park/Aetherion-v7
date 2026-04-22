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
import re
import os
import threading
import warnings

try:
    import ollama  # noqa: F401
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    warnings.warn(
        "ollama not installed. LLM features will be disabled.", ImportWarning
    )


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
    from_agent: str
    to_agent: str
    task_id: str
    priority: Priority = Priority.MEDIUM
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace: List[str] = field(default_factory=list)

    def to_json(self) -> str:
        data = asdict(self)
        if isinstance(self.priority, Enum):
            data['priority'] = self.priority.value
        return json.dumps(data, indent=2, default=str)

    @classmethod
    def from_json(cls, data: str) -> AgentMessage:
        raw = json.loads(data)
        raw['priority'] = Priority(raw['priority'])
        return cls(**raw)

    def add_to_trace(self, agent_name: str) -> None:
        self.trace.append(agent_name)

    def create_reply(self, from_agent: str, payload: Dict[str, Any]) -> AgentMessage:
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
    """Unified interface to Ollama with confidence scoring and source comparison."""

    def __init__(self, model: str = None, temperature: float = 0.7):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.temperature = temperature
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self._client = None
        self._available = None
        self._lock = threading.Lock()
        self._logger = None

    def _get_logger(self):
        if self._logger is None:
            from utils.logger import AetherionLogger
            self._logger = AetherionLogger()
        return self._logger

    @property
    def client(self):
        with self._lock:
            if self._client is None:
                if (
                    not OLLAMA_AVAILABLE
                    or os.getenv("AETHERION_TEST_MODE") == "true"
                ):
                    self._available = False
                    return None
                try:
                    import ollama as ollama_module
                    self._client = ollama_module
                    self._client.list()
                    self._available = True
                except Exception as e:
                    self._available = False
                    self._get_logger().warning(f"Ollama not accessible: {e}")
            return self._client

    @property
    def available(self):
        if self._available is None:
            _ = self.client
        return self._available

    def generate(
        self, prompt: str, system: Optional[str] = None,
        model: Optional[str] = None, temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        if not self.available:
            return self._mock_response(prompt)

        model_name = model or self.model
        temp = temperature if temperature is not None else self.temperature

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat(
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
            self._get_logger().error(f"LLM generation error: {e}")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> Dict[str, Any]:
        return {
            "content": f"[MOCK] Ollama unavailable. Prompt: {prompt[:100]}...",
            "confidence": 0.3,
            "model": "mock",
            "usage": {"eval_count": 0, "prompt_eval_count": 0}
        }

    def _estimate_confidence(self, text: str) -> float:
        hedging_phrases = [
            "might", "could", "possibly", "maybe", "I think", "perhaps",
            "not sure", "uncertain", "likely", "probably", "may be"
        ]
        text_lower = text.lower()
        hedge_count = sum(1 for h in hedging_phrases if h in text_lower)
        confidence = max(0.3, 1.0 - (hedge_count * 0.1))
        return min(0.95, confidence)

    def compare_sources(self, claims: List[Dict[str, str]]) -> Dict[str, Any]:
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
            json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        return {
            "consensus": None,
            "top_3_sources": list(range(min(3, len(claims)))),
            "confidence": 0.3
        }

    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> Dict[str, Any]:
        if not self.available:
            return self._mock_response(messages[-1]["content"])
        model_name = model or self.model
        try:
            response = self.client.chat(model=model_name, messages=messages)
            content = response["message"]["content"]
            confidence = self._estimate_confidence(content)
            return {
                "content": content,
                "confidence": confidence,
                "model": model_name,
                "usage": {"eval_count": response.get("eval_count", 0)}
            }
        except Exception as e:
            self._get_logger().error(f"Chat error: {e}")
            return self._mock_response(messages[-1]["content"])

    def embed(self, text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
        if not self.available:
            return None
        try:
            response = self.client.embeddings(model=model, prompt=text)
            return response["embedding"]
        except Exception:
            return None


class StrictLLMWrapper(LLMWrapper):
    """LLM wrapper that enforces structured output via Ollama tool-calling."""

    def generate_structured(self, prompt: str, schema: Dict, system: str = None) -> Dict:
        tool = {
            "type": "function",
            "function": {
                "name": "respond_with_structured_output",
                "description": "Provide response in the exact required format",
                "parameters": schema
            }
        }

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat(
            model=self.model,
            messages=messages,
            tools=[tool],
            tool_choice={
                "type": "function",
                "function": {"name": "respond_with_structured_output"}
            }
        )

        if response["message"].get("tool_calls"):
            tool_call = response["message"]["tool_calls"][0]
            return {
                "data": tool_call["function"]["arguments"],
                "confidence": self._estimate_confidence(
                    response["message"].get("content", "")
                ),
                "model": self.model
            }
        raise ValueError("LLM did not produce structured output")


class ToolEnabledLLMWrapper(StrictLLMWrapper):
    """LLM wrapper that can invoke external tools via function calling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tools = {}

    def register_tool(self, name: str, func: callable, description: str, parameters: Dict):
        """Register a callable tool that the LLM can invoke."""
        self.tools[name] = {
            "func": func,
            "description": description,
            "parameters": parameters
        }

    def generate_with_tools(self, prompt: str, system: str = None) -> Dict:
        """Generate a response that may include tool calls."""
        tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"]
                }
            }
            for name, info in self.tools.items()
        ]

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
        )

        if response["message"].get("tool_calls"):
            tool_results = []
            for tool_call in response["message"]["tool_calls"]:
                func_name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                if func_name in self.tools:
                    result = self.tools[func_name]["func"](**args)
                    tool_results.append({"name": func_name, "result": result})
            return {
                "tool_calls": tool_results,
                "content": response["message"].get("content", "")
            }

        return {"content": response["message"].get("content", "")}


class MessageValidator:
    @staticmethod
    def validate(message: AgentMessage) -> bool:
        required = ['from_agent', 'to_agent', 'task_id']
        for field in required:
            if not getattr(message, field, None):
                return False
        return True

    @staticmethod
    def is_valid_json(data: str) -> bool:
        try:
            msg = AgentMessage.from_json(data)
            return MessageValidator.validate(msg)
        except Exception:
            return False


class ProtocolRegistry:
    def __init__(self):
        self.handlers: Dict[str, callable] = {}

    def register(self, agent_name: str, handler: callable) -> None:
        self.handlers[agent_name] = handler

    def route(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        handler = self.handlers.get(message.to_agent)
        if handler:
            return handler(message)
        return None

    def broadcast(self, message: AgentMessage, exclude: List[str] = None) -> Dict[str, Any]:
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


__all__ = [
    "Priority",
    "Verdict",
    "AgentMessage",
    "LLMWrapper",
    "StrictLLMWrapper",
    "ToolEnabledLLMWrapper",
    "MessageValidator",
    "ProtocolRegistry"
]
