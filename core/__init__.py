"""
Aetherion Core Module
Exports protocol, state management, and memory systems.
"""

from core.protocol import (
    AgentMessage,
    LLMWrapper,
    Priority,
    Verdict
)

from core.task_state import (
    TaskState,
    TaskContext,
    TaskStateManager,
    VALID_TRANSITIONS
)

from core.memory import (
    KnowledgeGraph,
    AgentReputation,
    Archivist,
    MemoryEntry
)

__all__ = [
    # Protocol
    "AgentMessage",
    "LLMWrapper",
    "Priority",
    "Verdict",
    # State
    "TaskState",
    "TaskContext",
    "TaskStateManager",
    "VALID_TRANSITIONS",
    # Memory
    "KnowledgeGraph",
    "AgentReputation",
    "Archivist",
    "MemoryEntry"
]
