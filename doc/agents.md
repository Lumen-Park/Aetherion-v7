```markdown
# Agent Roster & Architecture

Aetherion v3.4 includes **70+ specialised domain-expert agents** across 14 academic colleges. Each agent is a Python class inheriting from `CollegeAgent` and is dynamically selected by the Curator based on the task goal.

## How Agents Work

1. **Curator Selection** – The Curator agent analyses the user's goal and selects up to 5 relevant experts from the registry.
2. **Instantiation** – Agents can run in two modes:
   - **Monolithic**: Direct Python instantiation within the Celery worker.
   - **Microservice**: Each agent runs as an independent FastAPI container, called via HTTP.
3. **Analysis** – Each agent receives the goal and returns a structured assessment (JSON) with confidence, concerns, recommendations, and references.
4. **Synthesis** – The Synthesizer merges all expert findings into a unified research brief for the Council.

## Agent Colleges

| College | Agents | Focus |
|---------|--------|-------|
| **Natural Sciences** | 9 | Physics, Chemistry, Biology, Mathematics, Astronomy, Geology, Quantum Computing, Materials Science, Marine Biology |
| **Business & Economics** | 7 | Economics, Enterprise Architecture, Finance, Marketing, Legal/Compliance, Supply Chain, Blockchain |
| **Data & Analytics** | 5 | Data Science, Statistics, Geospatial, Forecasting, Operations Research |
| **Humanities** | 6 | History, Philosophy/Ethics, Sociology, Linguistics, Design, Cognitive Psychology |
| **Engineering** | 7 | Systems Architecture, Performance, DevOps, Network, Database, Robotics, Aerospace |
| **Health & Medicine** | 6 | Medical Doctor, Pharmacologist, Neuroscientist, Biomedical Engineer, Nutritionist, Geneticist |
| **Environment & Climate** | 8 | Climate Science, Ecology, Hydrology, Disaster Resilience, Circular Economy, Renewable Energy, Urban Planning, Agricultural Science |
| **Security & Defense** | 5 | Red Team, Cryptographer, Signals Intelligence, Privacy Officer, Cybersecurity Policy |
| **Law & Policy** | 4 | Patent Examiner, Regulatory Affairs, International Trade, Compliance |
| **Arts & Media** | 4 | Copywriter, Multimedia, Journalist, Localization |
| **Advanced Research** | 5 | Futurist, Systems Thinker, Interdisciplinary Bridge, Epistemologist, AI |
| **Research Tools** | 1 | ArXivAgent (live academic literature search) |
| **Experiment** | 3 | PythonDataAnalyst, HypothesisTester, ExternalTool |
| **Esoteric** | 4 | Theoretical Physics, Synthetic Biology, Game Theorist, Contrarian |

## Adding a New Agent

1. Open `agents/colleges/all_colleges.py`.
2. Add a new class:
```python
class MyNewAgent(CollegeAgent):
    college = "Your College"
    expertise = "Brief description"
    def _build_system_prompt(self) -> str:
        return "You are an expert in..."
```

1. Add the class name to COLLEGE_MAPPING at the bottom of the file.
2. Run python scripts/audit_agents.py to verify instantiation.
3. Optionally add it as a microservice by running python scripts/generate_agent_services.py.

Agent Microservices

Each agent can run as an independent container. Generate the Compose entries:

```bash
python scripts/generate_agent_services.py >> docker-compose.yml
```

Then scale independently:

```bash
docker-compose up --scale economistagent=3
```

The orchestrator calls agents via HTTP using the SyncAgentClient or AgentClient.

```

---
