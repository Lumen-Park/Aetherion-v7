```markdown
# User Guide

## Running Aetherion

### Docker (recommended)
```bash
git clone https://github.com/Lumen-Park/Aetherion-.git
cd Aetherion-
cp .env.example .env
docker-compose up
```

Open http://localhost:8000 for the dashboard.

Local CLI

```bash
pip install -r requirements.txt
python main.py --mode chat
```

Modes

Mode Command
Chat python main.py --mode chat
Pipeline python main.py --mode pipeline "Write a prime checker"
Lab python main.py --mode lab "Does sunlight affect growth?"
Invention python main.py --mode invent "Self-healing concrete"
Mission python main.py --mode mission
Autonomous python main.py --autonomous

Dashboard

· Login with OAuth or API key.
· Tasks – view pipeline progress and Council verdicts.
· Agents – browse/search the 70+ agent catalog.
· Council – live deliberation stream.
· Constitution Editor – customise judge rules.

Override

Admins can override a rejected task via CLI:

```bash
python main.py --override task_123 operator "reason"
```

Or via the Dashboard Admin panel.

```

---

### `doc/developer-guide.md`

```markdown
# Developer Guide

## Setup
```bash
git clone https://github.com/Lumen-Park/Aetherion-.git
cd Aetherion-
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Running Tests

```bash
pytest --cov=core --cov=agents/council --cov=agents/governance
```

Coverage must stay ≥60%.

Code Style

```bash
black agents/ core/ tests/ mission/ utils/ api/ --line-length 79
isort agents/ core/ tests/ mission/ utils/ api/
```

Adding a New Agent

1. Open agents/colleges/all_colleges.py
2. Add a new class:

```python
class MyNewAgent(CollegeAgent):
    college = "Your College"
    expertise = "Brief description"
    def _build_system_prompt(self) -> str:
        return "You are an expert in..."
```

1. Add the name to COLLEGE_MAPPING.
2. Run python scripts/audit_agents.py to verify instantiation.

CI/CD

GitHub Actions runs linting, security scanning, and tests on every push/PR.

```

---
