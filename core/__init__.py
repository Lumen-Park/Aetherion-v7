"""
Aetherion Core Module
Exports protocol, state management, and memory systems.
"""

from core.memory import AgentReputation, Archivist, KnowledgeGraph, MemoryEntry
from core.protocol import AgentMessage, LLMWrapper, Priority, Verdict
from core.task_state import (VALID_TRANSITIONS, TaskContext, TaskState,
                             TaskStateManager)

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
    "MemoryEntry",
]
