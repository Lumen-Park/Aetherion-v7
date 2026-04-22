from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from core.protocol import StrictLLMWrapper


class CollegeAgent(ABC):
    college: str = "Unknown"
    expertise: str = "General"

    def __init__(self, name: str, model: str = "llama3"):
        self.name = name
        self.llm = StrictLLMWrapper(model=model)
        self.system_prompt = self._build_system_prompt()

    @abstractmethod
    def _build_system_prompt(self) -> str:
        pass

    def analyze(
        self, query: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        schema = {
            "type": "object",
            "properties": {
                "assessment": {"type": "string"},
                "confidence": {"type": "number"},
                "concerns": {"type": "array", "items": {"type": "string"}},
                "recommendations": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["assessment", "confidence"],
        }
        prompt = f"As a {self.expertise} expert, analyze:\nQUERY: {query}\nCONTEXT: {context or 'None'}"
        return self.llm.generate_structured(
            prompt, schema, system=self.system_prompt
        )["data"]

    def __repr__(self):
        return f"<{self.name} ({self.college})>"
