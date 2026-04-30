"""
Agents Module
Governance, Council, Colleges, Pipeline, Improvement, Interfaces.
"""


# Lazy imports to avoid circular dependencies
def get_governance():
    from agents.governance import Curator, MetaOrchestrator

    return MetaOrchestrator, Curator


def get_council():
    from agents.council import AetherionCouncil

    return AetherionCouncil


def get_colleges():
    from agents.colleges import (
        AGENT_REGISTRY,
        COLLEGE_MAPPING,
        get_agent,
        list_all_agents,
    )

    return AGENT_REGISTRY, COLLEGE_MAPPING, get_agent, list_all_agents


def get_pipeline():
    from agents.pipeline import (
        Debugger,
        Developer,
        DocumentationAgent,
        GoalRefiner,
        Partner,
        Presenter,
        Reporter,
        Researcher,
        Scout,
        Synthesizer,
        Tester,
    )

    return (
        GoalRefiner,
        Researcher,
        Developer,
        Partner,
        Tester,
        Debugger,
        Reporter,
        Scout,
        Synthesizer,
        Presenter,
        DocumentationAgent,
    )


__all__ = ["get_governance", "get_council", "get_colleges", "get_pipeline"]
