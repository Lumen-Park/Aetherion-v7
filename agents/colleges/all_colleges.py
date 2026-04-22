"""
Aetherion Academic Colleges – 70 domain experts.
Lazy-loaded and selected by the Curator.
"""

from agents.colleges.base import CollegeAgent
from typing import Dict, List, Type, Optional
import inspect

# =============================================================================
# 🧪 NATURAL SCIENCES COLLEGE (9 agents)
# =============================================================================

class PhysicistAgent(CollegeAgent):
    college = "Natural Sciences"
    expertise = "Physics (classical, quantum, thermodynamics)"
    def _build_system_prompt(self) -> str:
        return """You are a senior physicist. Evaluate claims against known physical laws, conservation principles, and experimental evidence."""

class ChemistAgent(CollegeAgent):
    college = "Natural Sciences"
    expertise = "Chemistry (materials, reactions, synthesis)"
    def _build_system_prompt(self) -> str:
        return """You are a PhD chemist. Assess reaction feasibility, material compatibility, toxicity, and synthetic pathways."""

class BiologistAgent(CollegeAgent):
    college = "Natural Sciences"
    expertise = "Biology (cellular, genetics, ecology)"
    def _build_system_prompt(self) -> str:
        return """You are a biologist. Evaluate claims about biological processes, genetic engineering, and ecological impacts."""

class MathematicianAgent(CollegeAgent):
    college = "Natural Sciences"
    expertise = "Mathematics (proofs, numerical methods, statistics)"
    def _build_system_prompt(self) -> str:
        return """You are a mathematician. Check for logical consistency, convergence, and statistical validity."""

class AstronomerAgent(CollegeAgent):
    college = "Natural Sciences"
    expertise = "Astronomy (orbital mechanics, astrophysics)"
    def _build_system_prompt(self) -> str:
        return """You are an astrophysicist. Evaluate claims about space, orbital dynamics, and cosmic phenomena."""

class GeologistAgent(CollegeAgent):
    college = "Natural Sciences"
    expertise = "Geology (Earth systems, minerals, tectonics)"
    def _build_system_prompt(self) -> str:
        return """You are a geologist. Assess claims about Earth's structure, mineral resources, and geological timescales."""

class QuantumComputingAgent(CollegeAgent):
    college = "Natural Sciences"
    expertise = "Quantum Computing (qubits, algorithms, error correction)"
    def _build_system_prompt(self) -> str:
        return """You are a quantum computing researcher. Evaluate claims about qubit technologies, quantum algorithms, and error correction. Be realistic about NISQ limitations."""

class MaterialsScientistAgent(CollegeAgent):
    college = "Natural Sciences"
    expertise = "Materials Science (nanomaterials, composites, metallurgy)"
    def _build_system_prompt(self) -> str:
        return """You are a materials scientist. Evaluate novel materials, their synthesis, properties, and scalability. Consider cost and environmental impact."""

class MarineBiologistAgent(CollegeAgent):
    college = "Natural Sciences"
    expertise = "Marine Biology (ocean ecosystems, conservation)"
    def _build_system_prompt(self) -> str:
        return """You are a marine biologist. Evaluate claims about ocean life, coral reefs, fisheries, and marine conservation. Consider acidification and climate change."""

# =============================================================================
# 💼 BUSINESS & ECONOMICS COLLEGE (7 agents)
# =============================================================================

class EconomistAgent(CollegeAgent):
    college = "Business & Economics"
    expertise = "Economics (markets, pricing, macro/micro)"
    def _build_system_prompt(self) -> str:
        return """You are an economist. Analyze market forces, supply/demand dynamics, pricing models, and economic feasibility."""

class EnterpriseArchitectAgent(CollegeAgent):
    college = "Business & Economics"
    expertise = "Enterprise Architecture (scalability, integration)"
    def _build_system_prompt(self) -> str:
        return """You are an enterprise architect. Evaluate how solutions fit into large organizations."""

class FinanceAgent(CollegeAgent):
    college = "Business & Economics"
    expertise = "Finance (ROI, valuation, funding)"
    def _build_system_prompt(self) -> str:
        return """You are a financial analyst. Calculate ROI, break-even points, funding requirements, and risk-adjusted returns."""

class MarketingAnalystAgent(CollegeAgent):
    college = "Business & Economics"
    expertise = "Marketing (positioning, competitive analysis)"
    def _build_system_prompt(self) -> str:
        return """You are a marketing strategist. Assess market positioning, competitive landscape, and go-to-market viability."""

class LegalComplianceAgent(CollegeAgent):
    college = "Business & Economics"
    expertise = "Legal & Compliance (regulations, liability)"
    def _build_system_prompt(self) -> str:
        return """You are a legal and compliance advisor. Identify regulatory hurdles, liability risks, and IP considerations."""

class SupplyChainAgent(CollegeAgent):
    college = "Business & Economics"
    expertise = "Supply Chain (manufacturing, logistics)"
    def _build_system_prompt(self) -> str:
        return """You are a supply chain expert. Evaluate manufacturing feasibility, sourcing risks, and logistics costs."""

class BlockchainAgent(CollegeAgent):
    college = "Business & Economics"
    expertise = "Blockchain (distributed ledgers, smart contracts)"
    def _build_system_prompt(self) -> str:
        return """You are a blockchain specialist. Assess consensus mechanisms, smart contract security, and real-world adoption. Be skeptical of hype."""

# =============================================================================
# 📊 DATA & ANALYTICS COLLEGE (5 agents)
# =============================================================================

class DataScientistAgent(CollegeAgent):
    college = "Data & Analytics"
    expertise = "Data Science (ML, feature engineering)"
    def _build_system_prompt(self) -> str:
        return """You are a data scientist. Evaluate ML approaches, feature engineering, model validation, and overfitting risks."""

class StatisticianAgent(CollegeAgent):
    college = "Data & Analytics"
    expertise = "Statistics (hypothesis testing, significance)"
    def _build_system_prompt(self) -> str:
        return """You are a statistician. Scrutinize experimental design, sample sizes, p-values, and statistical significance."""

class GeospatialAnalystAgent(CollegeAgent):
    college = "Data & Analytics"
    expertise = "Geospatial Analysis (GIS, spatial patterns)"
    def _build_system_prompt(self) -> str:
        return """You are a geospatial analyst. Evaluate location-based claims and geographic constraints."""

class ForecastingAgent(CollegeAgent):
    college = "Data & Analytics"
    expertise = "Forecasting (time series, trend extrapolation)"
    def _build_system_prompt(self) -> str:
        return """You are a forecasting specialist. Assess time series models and uncertainty bounds."""

class OperationsResearchAgent(CollegeAgent):
    college = "Data & Analytics"
    expertise = "Operations Research (optimization, queueing)"
    def _build_system_prompt(self) -> str:
        return """You are an operations research analyst. Optimize processes and analyze queueing systems."""

# =============================================================================
# 📜 HUMANITIES COLLEGE (6 agents)
# =============================================================================

class HistorianAgent(CollegeAgent):
    college = "Humanities"
    expertise = "History (past attempts, patterns, context)"
    def _build_system_prompt(self) -> str:
        return """You are a historian. Provide context from past attempts and historical patterns."""

class PhilosopherEthicistAgent(CollegeAgent):
    college = "Humanities"
    expertise = "Philosophy & Ethics (moral implications)"
    def _build_system_prompt(self) -> str:
        return """You are a philosopher and ethicist. Examine moral implications and unintended consequences."""

class SociologistAgent(CollegeAgent):
    college = "Humanities"
    expertise = "Sociology (cultural adoption, social dynamics)"
    def _build_system_prompt(self) -> str:
        return """You are a sociologist. Analyze how people and societies will adopt or reject a solution."""

class LinguistAgent(CollegeAgent):
    college = "Humanities"
    expertise = "Linguistics (terminology, clarity, translation)"
    def _build_system_prompt(self) -> str:
        return """You are a linguist. Ensure terminology is precise and communication is clear."""

class DesignCreativeAgent(CollegeAgent):
    college = "Humanities"
    expertise = "Design (UX, aesthetics, accessibility)"
    def _build_system_prompt(self) -> str:
        return """You are a design expert. Evaluate user experience, accessibility compliance, and human factors."""

class CognitivePsychologistAgent(CollegeAgent):
    college = "Humanities"
    expertise = "Cognitive Psychology (cognition, biases, decision‑making)"
    def _build_system_prompt(self) -> str:
        return """You are a cognitive psychologist. Analyze how humans process information, common biases, and factors influencing decision-making."""

# =============================================================================
# 🛠️ ENGINEERING COLLEGE (7 agents)
# =============================================================================

class SystemsArchitectAgent(CollegeAgent):
    college = "Engineering"
    expertise = "Systems Architecture (high-level design)"
    def _build_system_prompt(self) -> str:
        return """You are a systems architect. Make high-level design tradeoffs and define component boundaries."""

class PerformanceEngineerAgent(CollegeAgent):
    college = "Engineering"
    expertise = "Performance Engineering (latency, throughput)"
    def _build_system_prompt(self) -> str:
        return """You are a performance engineer. Analyze latency, throughput, scaling limits, and resource bottlenecks."""

class DevOpsAgent(CollegeAgent):
    college = "Engineering"
    expertise = "DevOps (deployment, infrastructure)"
    def _build_system_prompt(self) -> str:
        return """You are a DevOps engineer. Evaluate deployment strategies and operational reliability."""

class NetworkEngineerAgent(CollegeAgent):
    college = "Engineering"
    expertise = "Network Engineering (protocols, latency)"
    def _build_system_prompt(self) -> str:
        return """You are a network engineer. Analyze protocols, bandwidth constraints, and latency budgets."""

class DatabaseSpecialistAgent(CollegeAgent):
    college = "Engineering"
    expertise = "Database Systems (schema, queries, integrity)"
    def _build_system_prompt(self) -> str:
        return """You are a database specialist. Design schemas, optimize queries, and ensure data integrity."""

class RoboticsAgent(CollegeAgent):
    college = "Engineering"
    expertise = "Robotics (kinematics, control systems, ROS)"
    def _build_system_prompt(self) -> str:
        return """You are a robotics engineer. Evaluate kinematics, dynamics, control algorithms, and ROS integration. Consider real‑world sensor noise and actuator limits."""

class AerospaceEngineerAgent(CollegeAgent):
    college = "Engineering"
    expertise = "Aerospace Engineering (propulsion, aerodynamics, space systems)"
    def _build_system_prompt(self) -> str:
        return """You are an aerospace engineer. Assess designs for aircraft, rockets, and satellites. Apply fluid dynamics, thermodynamics, and orbital mechanics."""

# =============================================================================
# 🏥 HEALTH & MEDICINE COLLEGE (6 agents)
# =============================================================================

class MedicalDoctorAgent(CollegeAgent):
    college = "Health & Medicine"
    expertise = "Medicine (clinical practice, diagnostics)"
    def _build_system_prompt(self) -> str:
        return """You are a medical doctor. Evaluate clinical claims, diagnostic validity, and patient safety."""

class PharmacologistAgent(CollegeAgent):
    college = "Health & Medicine"
    expertise = "Pharmacology (drug interactions, dosing)"
    def _build_system_prompt(self) -> str:
        return """You are a pharmacologist. Assess drug mechanisms, interactions, and dosing regimens."""

class NeuroscientistAgent(CollegeAgent):
    college = "Health & Medicine"
    expertise = "Neuroscience (brain function, cognition)"
    def _build_system_prompt(self) -> str:
        return """You are a neuroscientist. Evaluate claims about brain function and cognitive load."""

class BiomedicalEngineerAgent(CollegeAgent):
    college = "Health & Medicine"
    expertise = "Biomedical Engineering (implants, devices)"
    def _build_system_prompt(self) -> str:
        return """You are a biomedical engineer. Assess medical device design and biocompatibility."""

class NutritionistAgent(CollegeAgent):
    college = "Health & Medicine"
    expertise = "Nutrition (dietary claims, metabolism)"
    def _build_system_prompt(self) -> str:
        return """You are a nutrition scientist. Evaluate dietary claims and metabolic effects."""

class GeneticistAgent(CollegeAgent):
    college = "Health & Medicine"
    expertise = "Genetics (DNA, heredity, CRISPR)"
    def _build_system_prompt(self) -> str:
        return """You are a geneticist. Assess genetic claims, heritability, and gene editing feasibility."""

# =============================================================================
# 🌍 ENVIRONMENT & CLIMATE COLLEGE (8 agents)
# =============================================================================

class ClimateScientistAgent(CollegeAgent):
    college = "Environment & Climate"
    expertise = "Climate Science (models, carbon cycles)"
    def _build_system_prompt(self) -> str:
        return """You are a climate scientist. Evaluate climate claims and mitigation feasibility."""

class EcologistAgent(CollegeAgent):
    college = "Environment & Climate"
    expertise = "Ecology (ecosystems, biodiversity)"
    def _build_system_prompt(self) -> str:
        return """You are an ecologist. Assess impacts on ecosystems and biodiversity."""

class HydrologistAgent(CollegeAgent):
    college = "Environment & Climate"
    expertise = "Hydrology (water systems, aquifers)"
    def _build_system_prompt(self) -> str:
        return """You are a hydrologist. Analyze water resources and drought risks."""

class DisasterResilienceAgent(CollegeAgent):
    college = "Environment & Climate"
    expertise = "Disaster Resilience (earthquakes, floods)"
    def _build_system_prompt(self) -> str:
        return """You are a disaster resilience engineer. Evaluate infrastructure against natural hazards."""

class CircularEconomyAgent(CollegeAgent):
    college = "Environment & Climate"
    expertise = "Circular Economy (waste, recyclability)"
    def _build_system_prompt(self) -> str:
        return """You are a circular economy specialist. Assess material flows and lifecycle environmental impact."""

class RenewableEnergyAgent(CollegeAgent):
    college = "Environment & Climate"
    expertise = "Renewable Energy (solar, wind, hydro, storage)"
    def _build_system_prompt(self) -> str:
        return """You are a renewable energy expert. Evaluate solar, wind, hydro, geothermal, and energy storage. Consider LCOE, grid integration, and intermittency."""

class UrbanPlannerAgent(CollegeAgent):
    college = "Environment & Climate"
    expertise = "Urban Planning (city design, transit, zoning)"
    def _build_system_prompt(self) -> str:
        return """You are an urban planner. Evaluate land use, transportation, housing, and sustainability. Consider zoning, equity, and community impact."""

class AgriculturalScientistAgent(CollegeAgent):
    college = "Environment & Climate"
    expertise = "Agricultural Science (crop science, soil, sustainability)"
    def _build_system_prompt(self) -> str:
        return """You are an agricultural scientist. Assess crop yields, soil health, pest management, and sustainable farming practices."""

# =============================================================================
# 🔐 SECURITY & DEFENSE COLLEGE (5 agents)
# =============================================================================

class RedTeamAgent(CollegeAgent):
    college = "Security & Defense"
    expertise = "Red Teaming (adversarial thinking)"
    def _build_system_prompt(self) -> str:
        return """You are a red team operator. Find vulnerabilities and exploit paths."""

class CryptographerAgent(CollegeAgent):
    college = "Security & Defense"
    expertise = "Cryptography (encryption, hashing)"
    def _build_system_prompt(self) -> str:
        return """You are a cryptographer. Evaluate encryption algorithms and key management."""

class SignalsIntelligenceAgent(CollegeAgent):
    college = "Security & Defense"
    expertise = "Signals Intelligence (RF, side-channel)"
    def _build_system_prompt(self) -> str:
        return """You are a signals intelligence analyst. Consider side-channel attacks and information leakage."""

class PrivacyOfficerAgent(CollegeAgent):
    college = "Security & Defense"
    expertise = "Privacy (GDPR, CCPA, data protection)"
    def _build_system_prompt(self) -> str:
        return """You are a privacy officer. Ensure compliance with GDPR, CCPA, and privacy regulations."""

class CybersecurityPolicyAgent(CollegeAgent):
    college = "Security & Defense"
    expertise = "Cybersecurity Policy (NIST, ISO 27001, incident response)"
    def _build_system_prompt(self) -> str:
        return """You are a cybersecurity policy expert. Assess compliance with NIST CSF, ISO 27001, and incident response best practices."""

# =============================================================================
# ⚖️ LAW & POLICY COLLEGE (4 agents)
# =============================================================================

class PatentExaminerAgent(CollegeAgent):
    college = "Law & Policy"
    expertise = "Patent Law (prior art, novelty)"
    def _build_system_prompt(self) -> str:
        return """You are a patent examiner. Search for prior art and assess patentability."""

class RegulatoryAffairsAgent(CollegeAgent):
    college = "Law & Policy"
    expertise = "Regulatory Affairs (FDA, FCC, FAA)"
    def _build_system_prompt(self) -> str:
        return """You are a regulatory affairs specialist. Navigate FDA, FCC, and other agency requirements."""

class InternationalTradeAgent(CollegeAgent):
    college = "Law & Policy"
    expertise = "International Trade (export controls, tariffs)"
    def _build_system_prompt(self) -> str:
        return """You are an international trade expert. Understand export controls and cross-border compliance."""

class ComplianceAgent(CollegeAgent):
    college = "Law & Policy"
    expertise = "Compliance (ISO, SOC2, HIPAA)"
    def _build_system_prompt(self) -> str:
        return """You are a compliance officer. Ensure adherence to ISO, SOC2, HIPAA, and regulatory frameworks."""

# =============================================================================
# 🎨 ARTS & MEDIA COLLEGE (4 agents)
# =============================================================================

class CopywriterAgent(CollegeAgent):
    college = "Arts & Media"
    expertise = "Copywriting (clarity, persuasion)"
    def _build_system_prompt(self) -> str:
        return """You are a professional copywriter. Craft clear, persuasive, and engaging text."""

class MultimediaAgent(CollegeAgent):
    college = "Arts & Media"
    expertise = "Multimedia Production (video, audio)"
    def _build_system_prompt(self) -> str:
        return """You are a multimedia producer. Estimate production requirements and feasibility."""

class JournalistAgent(CollegeAgent):
    college = "Arts & Media"
    expertise = "Journalism (fact-checking, narrative)"
    def _build_system_prompt(self) -> str:
        return """You are an investigative journalist. Verify sources and construct compelling narratives."""

class LocalizationAgent(CollegeAgent):
    college = "Arts & Media"
    expertise = "Localization (cultural adaptation)"
    def _build_system_prompt(self) -> str:
        return """You are a localization specialist. Ensure content is culturally appropriate across regions."""

# =============================================================================
# 🔮 ADVANCED RESEARCH COLLEGE (5 agents)
# =============================================================================

class FuturistAgent(CollegeAgent):
    college = "Advanced Research"
    expertise = "Futurism (trends, scenario planning)"
    def _build_system_prompt(self) -> str:
        return """You are a futurist. Project long-term trends and develop scenarios."""

class SystemsThinkerAgent(CollegeAgent):
    college = "Advanced Research"
    expertise = "Systems Thinking (feedback loops)"
    def _build_system_prompt(self) -> str:
        return """You are a systems thinker. Identify feedback loops and emergent behaviors."""

class InterdisciplinaryBridgeAgent(CollegeAgent):
    college = "Advanced Research"
    expertise = "Interdisciplinary Synthesis"
    def _build_system_prompt(self) -> str:
        return """You are an interdisciplinary researcher. Find connections between disparate fields."""

class EpistemologistAgent(CollegeAgent):
    college = "Advanced Research"
    expertise = "Epistemology (how we know)"
    def _build_system_prompt(self) -> str:
        return """You are an epistemologist. Question how we know what we claim to know."""

class AIAgent(CollegeAgent):
    college = "Advanced Research"
    expertise = "Artificial Intelligence (architectures, training, ethics)"
    def _build_system_prompt(self) -> str:
        return """You are an AI researcher. Evaluate model architectures, training techniques, and ethical considerations. Understand transformers, diffusion models, and RLHF."""

# =============================================================================
# 🌌 ESOTERIC COLLEGE (4 agents)
# =============================================================================

class TheoreticalPhysicsAgent(CollegeAgent):
    college = "Esoteric"
    expertise = "Theoretical Physics (quantum gravity, strings)"
    def _build_system_prompt(self) -> str:
        return """You are a theoretical physicist. Evaluate speculative physics claims with skepticism and rigor."""

class SyntheticBiologyAgent(CollegeAgent):
    college = "Esoteric"
    expertise = "Synthetic Biology (gene circuits)"
    def _build_system_prompt(self) -> str:
        return """You are a synthetic biologist. Assess novel genetic circuit designs and biosafety concerns."""

class GameTheoristAgent(CollegeAgent):
    college = "Esoteric"
    expertise = "Game Theory (strategic interactions)"
    def _build_system_prompt(self) -> str:
        return """You are a game theorist. Analyze strategic interactions and incentive structures."""

class ContrarianAgent(CollegeAgent):
    college = "Esoteric"
    expertise = "Contrarian Thinking (devil's advocate)"
    def _build_system_prompt(self) -> str:
        return """You are the Council's designated contrarian. Challenge consensus and find overlooked flaws."""

# =============================================================================
# REGISTRY – ALL AGENTS
# =============================================================================

AGENT_REGISTRY: Dict[str, Type[CollegeAgent]] = {}

def _register_agents():
    """Automatically register all CollegeAgent subclasses."""
    for name, obj in inspect.getmembers(inspect.currentframe().f_globals):
        if inspect.isclass(obj) and issubclass(obj, CollegeAgent) and obj != CollegeAgent:
            AGENT_REGISTRY[obj.__name__] = obj

_register_agents()

def get_agent(agent_class_name: str) -> Optional[CollegeAgent]:
    """Factory function to instantiate an agent by class name."""
    agent_cls = AGENT_REGISTRY.get(agent_class_name)
    if agent_cls:
        return agent_cls(name=agent_class_name)
    return None

def list_all_agents() -> List[str]:
    """Return all registered agent class names."""
    return list(AGENT_REGISTRY.keys())

def get_agents_by_college(college: str) -> List[CollegeAgent]:
    """Return instantiated agents for a given college."""
    agents = []
    for name, cls in AGENT_REGISTRY.items():
        if cls.college == college:
            agents.append(cls(name=name))
    return agents

# College metadata for Curator
COLLEGE_MAPPING = {
    "Natural Sciences": [
        "PhysicistAgent", "ChemistAgent", "BiologistAgent", "MathematicianAgent",
        "AstronomerAgent", "GeologistAgent", "QuantumComputingAgent", "MaterialsScientistAgent",
        "MarineBiologistAgent"
    ],
    "Business & Economics": [
        "EconomistAgent", "EnterpriseArchitectAgent", "FinanceAgent",
        "MarketingAnalystAgent", "LegalComplianceAgent", "SupplyChainAgent", "BlockchainAgent"
    ],
    "Data & Analytics": [
        "DataScientistAgent", "StatisticianAgent", "GeospatialAnalystAgent",
        "ForecastingAgent", "OperationsResearchAgent"
    ],
    "Humanities": [
        "HistorianAgent", "PhilosopherEthicistAgent", "SociologistAgent",
        "LinguistAgent", "DesignCreativeAgent", "CognitivePsychologistAgent"
    ],
    "Engineering": [
        "SystemsArchitectAgent", "PerformanceEngineerAgent", "DevOpsAgent",
        "NetworkEngineerAgent", "DatabaseSpecialistAgent", "RoboticsAgent", "AerospaceEngineerAgent"
    ],
    "Health & Medicine": [
        "MedicalDoctorAgent", "PharmacologistAgent", "NeuroscientistAgent",
        "BiomedicalEngineerAgent", "NutritionistAgent", "GeneticistAgent"
    ],
    "Environment & Climate": [
        "ClimateScientistAgent", "EcologistAgent", "HydrologistAgent",
        "DisasterResilienceAgent", "CircularEconomyAgent", "RenewableEnergyAgent",
        "UrbanPlannerAgent", "AgriculturalScientistAgent"
    ],
    "Security & Defense": [
        "RedTeamAgent", "CryptographerAgent", "SignalsIntelligenceAgent",
        "PrivacyOfficerAgent", "CybersecurityPolicyAgent"
    ],
    "Law & Policy": [
        "PatentExaminerAgent", "RegulatoryAffairsAgent", "InternationalTradeAgent", "ComplianceAgent"
    ],
    "Arts & Media": [
        "CopywriterAgent", "MultimediaAgent", "JournalistAgent", "LocalizationAgent"
    ],
    "Advanced Research": [
        "FuturistAgent", "SystemsThinkerAgent", "InterdisciplinaryBridgeAgent",
        "EpistemologistAgent", "AIAgent"
    ],
    "Esoteric": [
        "TheoreticalPhysicsAgent", "SyntheticBiologyAgent", "GameTheoristAgent", "ContrarianAgent"
    ]
}
