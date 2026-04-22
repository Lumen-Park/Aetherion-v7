"""
Mission Modes – Invention and Open Source.
"""

from mission.invention_pipeline import InventionPipeline

__all__ = [
    "InventionPipeline",
    "ScoutAgent",
    "FilterAgent",
    "SelectorAgent",
    "GitPayloadBuilder"
]


def __getattr__(name):
    if name in {"ScoutAgent", "FilterAgent", "SelectorAgent", "GitPayloadBuilder"}:
        from mission import mission_agent
        return getattr(mission_agent, name)
    raise AttributeError(f"module 'mission' has no attribute '{name}'")
