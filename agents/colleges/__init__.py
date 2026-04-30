"""
Academic Colleges – 70 domain experts.
"""

from agents.colleges.all_colleges import (
    AGENT_REGISTRY,
    COLLEGE_MAPPING,
    BiologistAgent,
    ChemistAgent,
    ClimateScientistAgent,
    DataScientistAgent,
    EconomistAgent,
    FuturistAgent,
    HistorianAgent,
    MathematicianAgent,
    MedicalDoctorAgent,
    PatentExaminerAgent,
    PhysicistAgent,
    RedTeamAgent,
    SystemsArchitectAgent,
    get_agent,
    get_agents_by_college,
    list_all_agents,
)
from agents.colleges.base import CollegeAgent

__all__ = [
    "CollegeAgent",
    "AGENT_REGISTRY",
    "COLLEGE_MAPPING",
    "get_agent",
    "list_all_agents",
    "get_agents_by_college",
    "PhysicistAgent",
    "ChemistAgent",
    "BiologistAgent",
    "MathematicianAgent",
    "EconomistAgent",
    "DataScientistAgent",
    "HistorianAgent",
    "SystemsArchitectAgent",
    "MedicalDoctorAgent",
    "ClimateScientistAgent",
    "RedTeamAgent",
    "PatentExaminerAgent",
    "FuturistAgent",
]
