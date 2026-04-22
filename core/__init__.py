"""
Aetherion Core Module
Exports protocol, state management, memory, and authentication.
"""

from core.protocol import (
    AgentMessage,
    LLMWrapper,
    Priority,
    Verdict,
    StrictLLMWrapper,
    ToolEnabledLLMWrapper,
)
from core.task_state import (
    TaskState,
    TaskContext,
    TaskStateManager,
    VALID_TRANSITIONS,
)
from core.memory import (
    KnowledgeGraph,
    AgentReputation,
    Archivist,
    MemoryEntry,
)
from core.auth import AuthManager

__all__ = [
    # Protocol
    "AgentMessage",
    "LLMWrapper",
    "Priority",
    "Verdict",
    "StrictLLMWrapper",
    "ToolEnabledLLMWrapper",
    # State
    "TaskState",
    "TaskContext",
    "TaskStateManager",
    "VALID_TRANSITIONS",
    # Memory
    "KnowledgeGraph",
    "AgentReputation",
    "Archivist",
    "MemoryEntry",
    # Auth
    "AuthManager",
]
