"""
Academic Colleges – 70 domain experts.
"""

from agents.colleges.base import CollegeAgent
from agents.colleges.all_colleges import (
    AGENT_REGISTRY,
    COLLEGE_MAPPING,
    get_agent,
    list_all_agents,
    get_agents_by_college,          
    PhysicistAgent,
    ChemistAgent,
    BiologistAgent,
    MathematicianAgent,
    EconomistAgent,
    DataScientistAgent,
    HistorianAgent,
    SystemsArchitectAgent,
    MedicalDoctorAgent,
    ClimateScientistAgent,
    RedTeamAgent,
    PatentExaminerAgent,
    FuturistAgent
)

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
    "FuturistAgent"
]
