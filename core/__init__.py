"""
Aetherion Core Module
Exports protocol, state management, memory, authentication, and OAuth.
"""

from core.auth import AuthManager
from core.memory import AgentReputation, Archivist, KnowledgeGraph, MemoryEntry
from core.oauth import OAuthManager, OIDCProvider
from core.protocol import (AgentMessage, LLMWrapper, Priority,
                           StrictLLMWrapper, ToolEnabledLLMWrapper, Verdict)
from core.task_state import (VALID_TRANSITIONS, TaskContext, TaskState,
                             TaskStateManager)

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
    # OAuth
    "OAuthManager",
    "OIDCProvider",
]
